import subprocess
import sys
import os
import time

def print_progress(step_name, current, total):
    percent = int((current / total) * 100)
    print(f"[{step_name}] Progress: {percent}%", end='\r')  # overwrite line

def run_floss_rank(sample_path, output_path=None):
    print("[+] Starting String Ranking Pipeline")

    # Step 1: Check file
    print("[+] Checking sample file...")
    if not os.path.isfile(sample_path):
        print(f"[!] Error: Sample not found: {sample_path}")
        return

    if output_path is None:
        output_path = sample_path + ".ranked_strings"
    print(f"[+] Output will be saved to: {output_path}")

    # Step 2: Run FLOSS
    print("[+] Running FLOSS to extract strings...")
    floss_cmd = ["floss", "-q", sample_path]

    try:
        floss_output = subprocess.check_output(floss_cmd, stderr=subprocess.DEVNULL, text=True)
    except Exception as e:
        print(f"[!] Error running FLOSS: {e}")
        return

    floss_lines = floss_output.splitlines()
    total_lines = len(floss_lines)

    if total_lines == 0:
        print("[!] No strings found to rank.")
        return

    print(f"[+] FLOSS finished. Extracted {total_lines} strings.")

    # Step 3: Rank strings with progress
    print("[+] Ranking strings with StringSifter...")

    try:
        rank_process = subprocess.Popen(
            ["rank_strings"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Feed strings line by line, updating percentage
        for idx, line in enumerate(floss_lines, 1):
            rank_process.stdin.write(line + "\n")
            if idx % max(1, total_lines // 100) == 0:
                print_progress("Ranking", idx, total_lines)
        rank_process.stdin.close()

        ranked_output, rank_err = rank_process.communicate()
        print_progress("Ranking", total_lines, total_lines)  # Ensure 100%
        print()  # Move to next line

        if rank_err:
            print(f"[!] Warning from rank_strings:\n{rank_err}")

    except Exception as e:
        print(f"[!] Error running rank_strings: {e}")
        return

    # Step 4: Save output
    print("[+] Saving ranked strings to file...")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ranked_output)
    except Exception as e:
        print(f"[!] Error writing output file: {e}")
        return

    print("[✓] Done! Ranked strings saved successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python floss_rank.py <sample.exe> [output_file]")
        sys.exit(1)

    sample = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    run_floss_rank(sample, output)
