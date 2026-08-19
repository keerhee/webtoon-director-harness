from pathlib import Path
import sys, yaml
config=yaml.safe_load(Path("config/quality_gate.yaml").read_text(encoding="utf-8"))
report=yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
weighted=sum(float(report["scores"][k])*float(w) for k,w in config["weights"].items())
hard=report.get("hard_failures",[])
print(f"Weighted score: {weighted:.2f}")
print(f"Threshold: {config['threshold']:.2f}")
print("PASS" if weighted>=config["threshold"] and not hard else "REVISE")
