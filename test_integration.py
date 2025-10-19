#!/usr/bin/env python3
"""Test PDF data loader integration"""

from data.pdf_loader import PDFDataLoader

# Test loading
print("🔄 Testing PDF Data Loader...")
loader = PDFDataLoader('data/Sample_data.pdf')

# Test methods
print(f"\n✅ Loaded {len(loader.df)} records")

print("\n📊 Current Metrics:")
metrics = loader.get_current_metrics()
for key, value in metrics.items():
    print(f"  - {key}: {value}")

print("\n🚢 Recent Vessels (first 3):")
vessels = loader.get_recent_vessels(3)
for v in vessels:
    print(f"  - {v.get('vessel_name')} (IMO: {v.get('imo_number')})")

print("\n🎯 Summary Stats:")
stats = loader.get_summary_stats()
for key, value in stats.items():
    print(f"  - {key}: {value}")

print("\n✅ All tests passed!")