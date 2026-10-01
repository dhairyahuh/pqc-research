#!/usr/bin/env python3
"""
Phase 2 Campaign Orchestrator
Executes systematic ML-KEM fault campaigns based on YAML configuration files
or runs the complete automated campaign suite.

Usage:
  python experiments/mlkem/run_campaign.py --config experiments/configurations/mlkem_phase2/ntt_stage_screening.yaml
  python experiments/mlkem/run_campaign.py --all
  python experiments/mlkem/run_campaign.py --analyze
"""

import argparse
import os
import subprocess
import sys
import yaml

def run_command(cmd, check=True):
    print(f"[*] Executing: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if check and res.returncode != 0:
        print(f"[-] Command failed with exit code {res.returncode}")
        sys.exit(res.returncode)
    return res.returncode

def ensure_binaries():
    runner = "bin/mlkem_campaign_runner"
    if not os.path.exists(runner):
        print("[*] Building bin/mlkem_campaign_runner via Makefile...")
        run_command("make bin/mlkem_campaign_runner")

def execute_config(config_path):
    print(f"=========================================================================")
    print(f" PHASE 2 CAMPAIGN ORCHESTRATOR — LOADING CONFIG: {config_path}")
    print(f"=========================================================================\n")
    
    if not os.path.exists(config_path):
        print(f"[-] Error: Configuration file not found: {config_path}")
        sys.exit(1)
        
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
        
    exp_id = cfg.get("experiment_id", "UNKNOWN")
    purpose = cfg.get("purpose", "")
    out_path = cfg.get("output_path", "results/phase2/raw/mlkem_campaign_raw_results.json")
    
    print(f"[+] Experiment ID: {exp_id}")
    print(f"[+] Purpose:       {purpose}")
    print(f"[+] Output Target: {out_path}\n")
    
    ensure_binaries()
    
    if "QUANT-ABSORPTION" in exp_id or "quantization" in config_path.lower():
        print("[*] Dispatching to Python Quantization Absorption Engine...")
        run_command("python3 experiments/mlkem/test_quantization_campaign.py")
    else:
        print(f"[*] Dispatching to Native C Campaign Runner: bin/mlkem_campaign_runner...")
        run_command(f"bin/mlkem_campaign_runner {out_path}")
        
    print("\n[*] Post-processing and updating sensitivity matrix & artifacts...")
    run_command("python3 experiments/mlkem/analyze_campaign_results.py")
    print(f"[+] Execution completed successfully for {exp_id}.\n")

def run_all():
    print("=========================================================================")
    print(" EXECUTING FULL PHASE 2 SYSTEMATIC ML-KEM FAULT CAMPAIGN")
    print("=========================================================================\n")
    ensure_binaries()
    run_command("bin/mlkem_campaign_runner results/phase2/raw/mlkem_campaign_raw_results.json")
    run_command("python3 experiments/mlkem/test_quantization_campaign.py")
    run_command("python3 experiments/mlkem/analyze_campaign_results.py")
    print("=========================================================================\n")
    print(" >>> ALL PHASE 2 CAMPAIGNS & ANALYSIS COMPLETE <<<")
    print("=========================================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Systematic ML-KEM Fault Campaign Runner (Phase 2)")
    parser.add_argument("--config", type=str, help="Path to YAML experiment configuration file")
    parser.add_argument("--all", action="store_true", help="Run all Phase 2 campaigns and generate all artifacts")
    parser.add_argument("--analyze", action="store_true", help="Re-analyze existing raw data and regenerate artifacts")
    
    args = parser.parse_args()
    
    if args.config:
        execute_config(args.config)
    elif args.all:
        run_all()
    elif args.analyze:
        run_command("python3 experiments/mlkem/analyze_campaign_results.py")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
