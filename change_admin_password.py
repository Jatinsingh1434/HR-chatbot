import os
from pathlib import Path

def change_admin_password():
    print("=" * 50)
    print(" TalentScout - Admin Password Management ")
    print("=" * 50)
    print()
    
    new_password = input("Enter the new Admin Password: ").strip()
    if not new_password:
        print("Password cannot be empty. Operation aborted.")
        return
        
    env_path = Path(".env")
    env_content = []
    updated = False
    
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            env_content = f.readlines()
            
    with open(env_path, "w", encoding="utf-8") as f:
        for line in env_content:
            if line.startswith("ADMIN_PASSWORD="):
                f.write(f"ADMIN_PASSWORD={new_password}\n")
                updated = True
            else:
                f.write(line)
        
        if not updated:
            if env_content and not env_content[-1].endswith("\n"):
                f.write("\n")
            f.write(f"ADMIN_PASSWORD={new_password}\n")
            
    print(f"\n✅ Password successfully updated in {env_path.absolute()}.")
    print("The system will now use the new password for the Streamlit Admin Dashboard.")

if __name__ == "__main__":
    change_admin_password()
