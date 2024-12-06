import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Load the CSV files for all tags
tags = ["r5.10.3"]
data = {tag: pd.read_csv(f"junit5-{tag}.csv") for tag in tags}

# Step 2: Filter for `org.junit.*` classes
def filter_production_classes(df):
    return df[df['Name'].str.contains("org.junit") & 
              df['Kind'].isin(['Private Class', 'Public Class', 'Private Method', 'Public Method', 'Protected Method'])]

filtered_data = {tag: filter_production_classes(data[tag]) for tag in tags}

# Step 3: Compute the number of classes and methods for each type
def compute_counts(df):
    class_counts = df[df['Kind'].isin(['Private Class', 'Public Class'])]['Kind'].value_counts()
    method_counts = df[df['Kind'].isin(['Private Method', 'Public Method', 'Protected Method'])]['Kind'].value_counts()
    return class_counts, method_counts

counts = {tag: compute_counts(filtered_data[tag]) for tag in tags}

# Step 4: Analyze metrics and generate box plots
metrics = ["SumCyclomatic", "AvgEssential", "MaxInheritanceTree", "PercentLackOfCohesion",
           "CountClassDerived", "CountClassCoupled", "CountDeclMethod", "Essential", "CountLineCode"]

def analyze_metrics(df, tag):
    analysis = {}
    for metric in metrics:
        if metric in df.columns:
            values = df[metric].dropna()
            analysis[metric] = {
                'median': values.median(),
                '50_percent_range': (values.quantile(0.25), values.quantile(0.75)),
                'min': values.min(),
                'max': values.max()
            }
    return analysis

analysis_results = {tag: analyze_metrics(filtered_data[tag], tag) for tag in tags}

def plot_boxplot(df, tag, metric, kind_filter):
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df[df['Kind'].isin(kind_filter)], x="Kind", y=metric)
    plt.title(f"{metric} Distribution ({tag})")
    plt.savefig(f"{tag}_{metric}_boxplot.png")

# Generate box plots for size and complexity metrics at method level
method_metrics = ["SumCyclomatic", "Essential", "CountLineCode"]
for tag, df in filtered_data.items():
    for metric in method_metrics:
        if metric in df.columns:
            plot_boxplot(df, tag, metric, ['Private Method', 'Public Method', 'Protected Method'])

# Step 5: Identify top 5 methods with the highest SLOC and complexity values
def top_5_methods(df, tag):
    results = {}
    for metric in ["CountLineCode", "SumCyclomatic"]:
        if metric in df.columns:
            top_5 = df.nlargest(5, metric)[["Name", metric]]
            results[metric] = top_5
    return results

top_methods = {tag: top_5_methods(filtered_data[tag], tag) for tag in tags}

# Step 6: Save the filtered data and analysis results
for tag, df in filtered_data.items():
    df.to_csv(f"{tag}_filtered.csv", index=False)

with open("analysis_results.txt", "w") as f:
    for tag, analysis in analysis_results.items():
        f.write(f"\n--- Analysis for {tag} ---\n")
        for metric, stats in analysis.items():
            f.write(f"{metric}: {stats}\n")

for tag, results in top_methods.items():
    for metric, data in results.items():
        data.to_csv(f"{tag}_top5_{metric}.csv", index=False)

# Step 7: Compute the number of classes for each type and save to a separate file
def compute_class_type_counts(df, tag):
    class_type_counts = df[df['Kind'].isin(['Private Class', 'Public Class'])]['Kind'].value_counts()
    class_type_counts.to_csv(f"{tag}_class_type_counts.csv", header=["Count"])

for tag, df in filtered_data.items():
    compute_class_type_counts(df, tag)
