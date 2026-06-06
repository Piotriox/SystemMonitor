// SystemMonitor backend.
// Exposes system resource metrics and the running process list to the frontend
// through Tauri commands. A single long-lived `System` is kept in managed state
// so that CPU usage and network rates can be computed as deltas between polls.

use std::sync::Mutex;
use std::time::Instant;

use serde::Serialize;
use sysinfo::{Disks, Networks, ProcessesToUpdate, System};

// Long-lived, shared monitoring state.
struct MonitorState {
    sys: Mutex<System>,
    networks: Mutex<Networks>,
    last_net_instant: Mutex<Instant>,
    // GPU name is detected once (it does not change at runtime) and cached.
    gpu_name: Mutex<Option<String>>,
}

#[derive(Serialize)]
struct CpuInfo {
    model: String,
    usage: f32,        // Global CPU usage percentage (0-100).
    cores: Vec<f32>,   // Per-core usage percentage.
    logical_cores: usize,
    physical_cores: usize,
    frequency_mhz: u64,
    base_frequency_mhz: Option<u64>,
    max_frequency_mhz: Option<u64>,
    temp_celsius: Option<f32>,
    cache_l1_mb: Option<u64>,
    cache_l2_mb: Option<u64>,
    cache_l3_mb: Option<u64>,
    vendor: String,
}

#[derive(Serialize)]
struct GpuInfo {
    name: String,
    vendor: String,
    vram_mb: Option<u64>,
    driver_version: Option<String>,
}

#[derive(Serialize)]
struct MemoryInfo {
    total: u64,        // Bytes.
    used: u64,         // Bytes.
    available: u64,    // Bytes.
    usage: f32,        // Percentage (0-100).
    speed_mhz: Option<u64>,
    memory_type: Option<String>,
}

#[derive(Serialize)]
struct DiskInfo {
    name: String,
    mount_point: String,
    file_system: String,
    disk_type: String,    // SSD, HDD, etc.
    model: String,        // Disk model/serial.
    total: u64,        // Bytes.
    available: u64,    // Bytes.
    used: u64,         // Bytes.
    usage: f32,        // Percentage (0-100).
}

#[derive(Serialize)]
struct NetworkInfo {
    interface: String,
    down_rate: f64,        // Bytes per second since the previous poll.
    up_rate: f64,          // Bytes per second since the previous poll.
    total_received: u64,   // Bytes.
    total_transmitted: u64, // Bytes.
}

#[derive(Serialize)]
struct Resources {
    cpu: CpuInfo,
    gpu: GpuInfo,
    memory: MemoryInfo,
    disks: Vec<DiskInfo>,
    networks: Vec<NetworkInfo>,
}

#[derive(Serialize)]
struct ProcessInfo {
    pid: u32,
    name: String,
    cpu_usage: f32,    // Percentage (can exceed 100 on multi-core systems).
    memory: u64,       // Bytes.
    status: String,
}

// Collect a full resource snapshot for the Resources view.
#[tauri::command]
fn get_resources(state: tauri::State<MonitorState>) -> Resources {
    // --- CPU + memory ---
    let (cpu, memory) = {
        let mut sys = state.sys.lock().unwrap();
        sys.refresh_cpu_all();
        sys.refresh_memory();

        let cpus = sys.cpus();
        let model = cpus
            .first()
            .map(|c| c.brand().trim().to_string())
            .filter(|s| !s.is_empty())
            .unwrap_or_else(|| "Unknown CPU".to_string());
        let frequency_mhz = cpus.first().map(|c| c.frequency()).unwrap_or(0);
        let cores: Vec<f32> = cpus.iter().map(|c| c.cpu_usage()).collect();
        let logical_cores = cores.len();
        let vendor = extract_cpu_vendor(&model);
        let temp_celsius = detect_cpu_temp(&sys);

        // Physical cores detection (best effort)
        let physical_cores = sys.physical_core_count().unwrap_or(logical_cores / 2).max(1);

        let cpu = CpuInfo {
            model,
            usage: sys.global_cpu_usage(),
            logical_cores,
            physical_cores,
            cores,
            frequency_mhz,
            base_frequency_mhz: None, // Not available in sysinfo
            max_frequency_mhz: Some(frequency_mhz),
            temp_celsius,
            cache_l1_mb: None, // Not available in sysinfo
            cache_l2_mb: None, // Not available in sysinfo
            cache_l3_mb: None, // Not available in sysinfo
            vendor,
        };

        let total = sys.total_memory();
        let used = sys.used_memory();
        let available = sys.available_memory();
        let usage = if total > 0 {
            (used as f64 / total as f64 * 100.0) as f32
        } else {
            0.0
        };
        let (speed_mhz, memory_type) = detect_memory_info();
        let memory = MemoryInfo {
            total,
            used,
            available,
            usage,
            speed_mhz,
            memory_type,
        };

        (cpu, memory)
    };

    // --- GPU (cached name) ---
    let gpu = {
        let mut cached = state.gpu_name.lock().unwrap();
        if cached.is_none() {
            *cached = Some(detect_gpu_name());
        }
        let gpu_name = cached.clone().unwrap_or_else(|| "Unknown GPU".to_string());
        let (vendor, vram_mb) = extract_gpu_info(&gpu_name);
        let driver_version = detect_gpu_driver_version();
        GpuInfo {
            name: gpu_name,
            vendor,
            vram_mb,
            driver_version,
        }
    };

    // --- Disks (fresh snapshot each call) ---
    let disk_list = Disks::new_with_refreshed_list();
    let mut disks = Vec::new();
    for disk in disk_list.list() {
        let total = disk.total_space();
        let available = disk.available_space();
        let used = total.saturating_sub(available);
        let usage = if total > 0 {
            (used as f64 / total as f64 * 100.0) as f32
        } else {
            0.0
        };
        let disk_type = format!("{:?}", disk.kind());
        disks.push(DiskInfo {
            name: disk.name().to_string_lossy().to_string(),
            mount_point: disk.mount_point().to_string_lossy().to_string(),
            file_system: disk.file_system().to_string_lossy().to_string(),
            disk_type,
            model: disk.name().to_string_lossy().to_string(),
            total,
            available,
            used,
            usage,
        });
    }

    // --- Networks (delta-based rate) ---
    let networks = {
        let mut nets = state.networks.lock().unwrap();
        nets.refresh();

        let mut last = state.last_net_instant.lock().unwrap();
        let now = Instant::now();
        let elapsed = now.duration_since(*last).as_secs_f64().max(0.001);
        *last = now;

        let mut out = Vec::new();
        for (interface, data) in &*nets {
            out.push(NetworkInfo {
                interface: interface.clone(),
                down_rate: data.received() as f64 / elapsed,
                up_rate: data.transmitted() as f64 / elapsed,
                total_received: data.total_received(),
                total_transmitted: data.total_transmitted(),
            });
        }
        out
    };

    Resources {
        cpu,
        gpu,
        memory,
        disks,
        networks,
    }
}

// Collect the running process list for the Processes view, sorted by CPU usage.
#[tauri::command]
fn get_processes(state: tauri::State<MonitorState>) -> Vec<ProcessInfo> {
    let mut sys = state.sys.lock().unwrap();
    sys.refresh_processes(ProcessesToUpdate::All);

    let mut list: Vec<ProcessInfo> = sys
        .processes()
        .iter()
        .map(|(pid, process)| ProcessInfo {
            pid: pid.as_u32(),
            name: process.name().to_string_lossy().to_string(),
            cpu_usage: process.cpu_usage(),
            memory: process.memory(),
            status: process.status().to_string(),
        })
        .collect();

    list.sort_by(|a, b| {
        b.cpu_usage
            .partial_cmp(&a.cpu_usage)
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    list
}

// Best-effort, platform-specific GPU name detection. Returns "Unknown GPU" on failure.
fn detect_gpu_name() -> String {
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        use std::process::Command;
        // Avoid flashing a console window when spawning PowerShell.
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        if let Ok(output) = Command::new("powershell")
            .args([
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
            ])
            .creation_flags(CREATE_NO_WINDOW)
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().map(|l| l.trim()).find(|l| !l.is_empty()) {
                    return line.to_string();
                }
            }
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        if let Ok(output) = Command::new("sh")
            .args(["-c", "lspci | grep -Ei 'vga|3d|display'"])
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().find(|l| !l.trim().is_empty()) {
                    // Example: "00:02.0 VGA compatible controller: Intel UHD Graphics 620"
                    if let Some(pos) = line.rfind(": ") {
                        return line[pos + 2..].trim().to_string();
                    }
                    return line.trim().to_string();
                }
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        if let Ok(output) = Command::new("sh")
            .args([
                "-c",
                "system_profiler SPDisplaysDataType | grep 'Chipset Model:'",
            ])
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().find(|l| l.contains("Chipset Model:")) {
                    if let Some(pos) = line.find(':') {
                        return line[pos + 1..].trim().to_string();
                    }
                }
            }
        }
    }

    "Unknown GPU".to_string()
}

// Extract CPU vendor from model string.
fn extract_cpu_vendor(model: &str) -> String {
    let model_lower = model.to_lowercase();
    if model_lower.contains("intel") {
        "Intel".to_string()
    } else if model_lower.contains("amd") {
        "AMD".to_string()
    } else if model_lower.contains("arm") {
        "ARM".to_string()
    } else if model_lower.contains("apple") {
        "Apple".to_string()
    } else {
        "Unknown".to_string()
    }
}

// Detect CPU temperature from system components.
fn detect_cpu_temp(_sys: &System) -> Option<f32> {
    // CPU temperature not available in sysinfo 0.31.4
    None
}

// Extract GPU vendor and detect VRAM from GPU name.
fn extract_gpu_info(gpu_name: &str) -> (String, Option<u64>) {
    let gpu_lower = gpu_name.to_lowercase();
    let vendor = if gpu_lower.contains("nvidia") {
        "NVIDIA".to_string()
    } else if gpu_lower.contains("amd") || gpu_lower.contains("radeon") {
        "AMD".to_string()
    } else if gpu_lower.contains("intel") {
        "Intel".to_string()
    } else if gpu_lower.contains("apple") {
        "Apple".to_string()
    } else {
        "Unknown".to_string()
    };

    // Try to extract VRAM from name (e.g., "RTX 3080 10GB")
    let vram = gpu_name
        .split_whitespace()
        .rev()
        .find_map(|word| {
            let word_lower = word.to_lowercase();
            if word_lower.ends_with("gb") || word_lower.ends_with("mb") {
                let num_str = if word_lower.ends_with("gb") {
                    &word_lower[..word_lower.len() - 2]
                } else {
                    &word_lower[..word_lower.len() - 2]
                };
                if word_lower.ends_with("gb") {
                    num_str.parse::<u64>().ok().map(|n| n * 1024)
                } else {
                    num_str.parse::<u64>().ok()
                }
            } else {
                None
            }
        });

    (vendor, vram)
}

// Detect GPU driver version (platform-specific).
fn detect_gpu_driver_version() -> Option<String> {
    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        use std::process::Command;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        if let Ok(output) = Command::new("powershell")
            .args([
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty DriverVersion",
            ])
            .creation_flags(CREATE_NO_WINDOW)
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().map(|l| l.trim()).find(|l| !l.is_empty()) {
                    return Some(line.to_string());
                }
            }
        }
    }

    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        // Try nvidia-smi first
        if let Ok(output) = Command::new("nvidia-smi")
            .arg("--query-gpu=driver_version")
            .arg("--format=csv,noheader")
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().find(|l| !l.trim().is_empty()) {
                    return Some(line.trim().to_string());
                }
            }
        }
    }

    None
}

// Detect RAM speed and type (platform-specific).
fn detect_memory_info() -> (Option<u64>, Option<String>) {
    #[cfg(target_os = "linux")]
    {
        use std::process::Command;
        let mut speed = None;
        let mut mem_type = None;

        // Try dmidecode for memory info
        if let Ok(output) = Command::new("sh")
            .args(["-c", "sudo dmidecode -t memory 2>/dev/null | grep -E 'Speed|Type'"])
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                for line in text.lines() {
                    if line.contains("Speed:") {
                        if let Some(speed_str) = line.split(':').nth(1) {
                            let speed_str = speed_str.trim();
                            if let Some(num_str) = speed_str.split_whitespace().next() {
                                speed = num_str.parse::<u64>().ok();
                            }
                        }
                    } else if line.contains("Type:") {
                        if let Some(type_str) = line.split(':').nth(1) {
                            mem_type = Some(type_str.trim().to_string());
                            break;
                        }
                    }
                }
            }
        }

        (speed, mem_type)
    }

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        use std::process::Command;
        let mut speed = None;
        let mut mem_type = None;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;

        // Try WMI for memory speed
        if let Ok(output) = Command::new("powershell")
            .args([
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_PhysicalMemory | Select-Object -ExpandProperty Speed",
            ])
            .creation_flags(CREATE_NO_WINDOW)
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().find(|l| !l.trim().is_empty()) {
                    speed = line.trim().parse::<u64>().ok();
                }
            }
        }

        // Try WMI for memory type
        if let Ok(output) = Command::new("powershell")
            .args([
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_PhysicalMemory | Select-Object -ExpandProperty MemoryType",
            ])
            .creation_flags(CREATE_NO_WINDOW)
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().find(|l| !l.trim().is_empty()) {
                    // Map WMI memory type codes to names
                    mem_type = Some(match line.trim() {
                        "2" => "DRAM".to_string(),
                        "3" => "SDRAM".to_string(),
                        "4" => "RDRAM".to_string(),
                        "5" => "DDR".to_string(),
                        "6" => "DDR2".to_string(),
                        "7" => "DDR2 FB-DIMM".to_string(),
                        "8" => "DDR3".to_string(),
                        "9" => "DDR4".to_string(),
                        "10" => "DDR5".to_string(),
                        code => format!("Unknown ({})", code),
                    });
                }
            }
        }

        (speed, mem_type)
    }

    #[cfg(target_os = "macos")]
    {
        use std::process::Command;
        let mut speed = None;

        // Try system_profiler for memory speed
        if let Ok(output) = Command::new("sh")
            .args(["-c", "system_profiler SPMemoryDataType | grep 'Speed'"])
            .output()
        {
            if let Ok(text) = String::from_utf8(output.stdout) {
                if let Some(line) = text.lines().next() {
                    if let Some(speed_part) = line.split(':').nth(1) {
                        let speed_str = speed_part.trim();
                        if let Some(num_str) = speed_str.split_whitespace().next() {
                            speed = num_str.parse::<u64>().ok();
                        }
                    }
                }
            }
        }

        (speed, None)
    }

    #[cfg(not(any(target_os = "linux", target_os = "windows", target_os = "macos")))]
    {
        (None, None)
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let state = MonitorState {
        sys: Mutex::new(System::new_all()),
        networks: Mutex::new(Networks::new_with_refreshed_list()),
        last_net_instant: Mutex::new(Instant::now()),
        gpu_name: Mutex::new(None),
    };

    tauri::Builder::default()
        .manage(state)
        .invoke_handler(tauri::generate_handler![get_resources, get_processes])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
