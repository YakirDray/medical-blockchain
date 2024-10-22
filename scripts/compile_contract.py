import json
import os
from solcx import compile_standard, install_solc
from pathlib import Path

def compile_contract():
    # התקנת גרסת solc
    install_solc('0.8.0')
    
    # קריאת קובץ החוזה
    contract_path = Path("contracts/MedicalRegistry.sol")
    with open(contract_path, "r", encoding="utf-8") as file:
        contract_source = file.read()

    # קומפילציה
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"MedicalRegistry.sol": {"content": contract_source}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.0",
    )

    # יצירת תיקיית build אם לא קיימת
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    # שמירת התוצאות
    with open(build_dir / "MedicalRegistry.json", "w") as file:
        json.dump(compiled_sol, file, indent=4)

    # שמירת ה-ABI בנפרד
    contract_abi = compiled_sol["contracts"]["MedicalRegistry.sol"]["MedicalRegistry"]["abi"]
    with open(build_dir / "contract_abi.json", "w") as file:
        json.dump(contract_abi, file, indent=4)

    print("Contract compiled successfully!")
    return compiled_sol

if __name__ == "__main__":
    compile_contract()