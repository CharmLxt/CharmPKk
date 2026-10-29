"""Безопасное чтение памяти процессов (Read-Only)."""
import ctypes
import platform
import os
import sys
import struct

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("cntUsage", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", ctypes.c_ulong),
        ("cntThreads", ctypes.c_ulong),
        ("th32ParentProcessID", ctypes.c_ulong),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", ctypes.c_ulong),
        ("szExeFile", ctypes.c_char * 260)
    ]

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("th32ModuleID", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("GlblcntUsage", ctypes.c_ulong),
        ("ProccntUsage", ctypes.c_ulong),
        ("modBaseAddr", ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize", ctypes.c_ulong),
        ("hModule", ctypes.c_void_p),
        ("szModule", ctypes.c_char * 256),
        ("szExePath", ctypes.c_char * 260)
    ]

class MemoryReader:
    """Класс для безопасного чтения памяти процессов (Read-Only)."""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        if self.is_windows:
            self.k32 = ctypes.windll.kernel32

    def get_pids(self, process_name):
        pids = []
        if self.is_windows:
            snapshot = self.k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
            if snapshot == -1:
                return pids
            
            entry = PROCESSENTRY32()
            entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
            
            if self.k32.Process32First(snapshot, ctypes.byref(entry)):
                while True:
                    name = entry.szExeFile.decode('utf-8', errors='ignore').lower()
                    if name == process_name.lower():
                        pids.append(entry.th32ProcessID)
                    if not self.k32.Process32Next(snapshot, ctypes.byref(entry)):
                        break
            self.k32.CloseHandle(snapshot)
        else:
            import subprocess
            try:
                out = subprocess.check_output(["pgrep", "-f", process_name]).decode().strip()
                pids = [int(p) for p in out.split('\n') if p]
            except Exception:
                pass
        return pids

    def get_base_address(self, pid, module_name):
        if self.is_windows:
            snapshot = self.k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
            if snapshot == -1:
                return None
            
            entry = MODULEENTRY32()
            entry.dwSize = ctypes.sizeof(MODULEENTRY32)
            
            base_addr = None
            if self.k32.Module32First(snapshot, ctypes.byref(entry)):
                while True:
                    name = entry.szModule.decode('utf-8', errors='ignore').lower()
                    if name == module_name.lower():
                        base_addr = ctypes.cast(entry.modBaseAddr, ctypes.c_void_p).value
                        break
                    if not self.k32.Module32Next(snapshot, ctypes.byref(entry)):
                        break
            self.k32.CloseHandle(snapshot)
            return base_addr
        else:
            try:
                with open(f"/proc/{pid}/maps", "r") as f:
                    for line in f:
                        if module_name in line:
                            return int(line.split("-")[0], 16)
            except Exception:
                pass
            return None

    def _open_process(self, pid):
        if not self.is_windows:
            return pid
        handle = self.k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
        return handle if handle != 0 else None

    def _close_process(self, handle):
        if self.is_windows and handle:
            self.k32.CloseHandle(handle)

    def read_memory(self, pid, address, size):
        handle = self._open_process(pid)
        if not handle:
            return None
        
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t(0)
        
        if self.is_windows:
            success = self.k32.ReadProcessMemory(
                handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(bytes_read)
            )
            self._close_process(handle)
            if success:
                return buffer.raw
        else:
            try:
                with open(f"/proc/{pid}/mem", "rb") as f:
                    f.seek(address)
                    return f.read(size)
            except Exception:
                pass
        return None

    def read_int(self, pid, address):
        data = self.read_memory(pid, address, 4)
        return struct.unpack("<i", data)[0] if data else None

    def read_float(self, pid, address):
        data = self.read_memory(pid, address, 4)
        return struct.unpack("<f", data)[0] if data else None
        
    def read_int64(self, pid, address):
        data = self.read_memory(pid, address, 8)
        return struct.unpack("<q", data)[0] if data else None

    def read_string(self, pid, address, max_len=256):
        data = self.read_memory(pid, address, max_len)
        return data.split(b'\x00')[0].decode('utf-8', errors='ignore') if data else None

    def read_pointer(self, pid, base_address, offsets):
        current_addr = base_address
        for offset in offsets:
            ptr = self.read_int64(pid, current_addr)
            if not ptr:
                return None
            current_addr = ptr + offset
        return current_addr

    def read_pointer_value(self, pid, base_address, offsets, data_type="int"):
        final_addr = self.read_pointer(pid, base_address, offsets)
        if not final_addr:
            return None
        if data_type == "int":
            return self.read_int(pid, final_addr)
        elif data_type == "float":
            return self.read_float(pid, final_addr)
        elif data_type == "string":
            return self.read_string(pid, final_addr)
        return None