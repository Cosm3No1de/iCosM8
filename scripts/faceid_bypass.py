#!/usr/bin/env python3
import os
import sys
import subprocess
from time import sleep

def main():
    print("[*] Iniciando bypass de Face ID...")
    
    # Verificar dispositivo en modo DFU
    try:
        check_dfu = subprocess.run(["irecovery", "-q"], capture_output=True, text=True)
        if "DFU" not in check_dfu.stdout:
            print("[-] Error: Dispositivo no está en modo DFU")
            return 1
            
        print("[*] Dispositivo en modo DFU detectado")
        
        # Enviar comandos para bypass
        print("[*] Enviando payload de bypass...")
        subprocess.run(["irecovery", "-f", "payloads/faceid_payload.bin"], check=True)
        
        print("[+] Bypass de Face ID completado con éxito!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"[-] Error en el proceso: {e}")
        return 1
    except Exception as e:
        print(f"[-] Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    if "--override" not in sys.argv:
        print("Este script debe ejecutarse desde la herramienta iCosM8")
        sys.exit(1)
    
    sys.exit(main())