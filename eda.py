import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import shapiro


df = pd.read_csv("Fitness_Tracker_Data.csv")
df['Date'] = pd.to_datetime(df['Date'])

# 1. Missing Values Check
print("Missing values per column:\n", df.isnull().sum())

# 4. Clean Workout_Type (strip spaces, fix case)
df['Workout_Type'] = df['Workout_Type'].str.strip().str.title()
print("Unique workout types after cleaning:", df['Workout_Type'].unique())

# 2. Handle zero or invalid Steps before ratio calculation
df.loc[df['Steps'] <= 0, 'Steps'] = np.nan

# Now safe to calculate Calories_per_Step
df['Calories_per_Step'] = df['Calories_Burned'] / df['Steps']

# 3. Detect outliers (for info)
def detect_outliers(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return series[(series < lower) | (series > upper)]

print(f"Steps outliers count: {len(detect_outliers(df['Steps'].dropna()))}")
print(f"Calories Burned outliers count: {len(detect_outliers(df['Calories_Burned'].dropna()))}")
print(f"Heart Rate outliers count: {len(detect_outliers(df['Heart_Rate_avg'].dropna()))}")

# 5. Check duplicate and missing dates
print(f"Duplicate Dates: {df['Date'].duplicated().sum()}")
full_dates = pd.date_range(start=df['Date'].min(), end=df['Date'].max())
missing_dates = full_dates.difference(df['Date'].unique())
print(f"Missing Dates: {missing_dates}")

# 6. Normality Test per workout type (example for Calories_Burned)
for workout in df['Workout_Type'].unique():
    data = df[df['Workout_Type'] == workout]['Calories_Burned'].dropna()
    if len(data) >= 3:
        stat, p = shapiro(data)
        print(f"Shapiro-Wilk p-value for {workout} Calories Burned: {p:.4f}")
    else:
        print(f"Not enough data for Shapiro test for {workout}")


# # 7. Check group sizes for statistical tests
# print("Workout Type group sizes:\n", df['Workout_Type'].value_counts())



print("Data Types:\n",df.dtypes)
print("\nFirst 5 Rows:\n",df.head())
print("Dataset Info:\n", df.info())
print("\nSummary Statistics:\n", df.describe())
print("\nWorkout Type Distribution:\n", df['Workout_Type'].value_counts())

# # Set plot style
# sns.set(style='whitegrid')
# plt.figure(figsize=(14, 10))

# # 1. Steps distribution
# plt.subplot(2, 2, 1)
# sns.histplot(df['Steps'], kde=True, color='skyblue')
# plt.title('Distribution of Steps')

# # 2. Heart rate boxplot


# plt.subplot(2, 2, 2)
# sns.boxplot(y=df['Heart_Rate_avg'], color='lightcoral')
# plt.title('Heart Rate Average - Boxplot')

# # 3. Scatter plot of Steps vs Calories Burned
# plt.subplot(2, 2, 3)
# sns.scatterplot(x='Steps', y='Calories_Burned', hue='Workout_Type', data=df)
# plt.title('Steps vs Calories Burned')

# # 4. Count plot of Workout Types
# plt.subplot(2, 2, 4)
# sns.countplot(x='Workout_Type', data=df, palette='pastel', order=df['Workout_Type'].value_counts().index)
# plt.title('Workout Type Distribution')

# plt.tight_layout()
# plt.show()


# Set plot style
sns.set(style='whitegrid')

# ---------- TRENDS ----------
# Daily averages
daily_summary = df.groupby('Date')[['Steps', 'Calories_Burned', 'Heart_Rate_avg']].mean()

# Plot trend over time
daily_summary.plot(title='Daily Averages: Steps, Calories Burned, Heart Rate', figsize=(12, 6))
plt.ylabel("Value")
plt.xlabel("Date")
plt.show()

# Steps vs Calories Burned
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Steps', y='Calories_Burned', hue='Workout_Type')
plt.title('Steps vs Calories Burned')
plt.show()

# ---------- PATTERNS ----------
# Calories per Step
df['Calories_per_Step'] = df['Calories_Burned'] / df['Steps']
plt.figure(figsize=(8, 6))
sns.boxplot(x='Workout_Type', y='Calories_per_Step', data=df)
plt.title('Calories per Step by Workout Type')
plt.show()

# Heart Rate by Workout Type
plt.figure(figsize=(8, 6))
sns.boxplot(x='Workout_Type', y='Heart_Rate_avg', data=df)
plt.title('Heart Rate by Workout Type')
plt.show()

# ---------- ANOMALIES ----------
# Steps outliers
plt.figure(figsize=(6, 4))
sns.boxplot(y=df['Steps'])
plt.title('Outliers in Steps')
plt.show()

# Calories outliers
plt.figure(figsize=(6, 4))
sns.boxplot(y=df['Calories_Burned'])
plt.title('Outliers in Calories Burned')
plt.show()

# Suspicious Heart Rate entries
print("Unusually Low Heart Rates:\n", df[df['Heart_Rate_avg'] < 50])
print("\nUnusually High Heart Rates:\n", df[df['Heart_Rate_avg'] > 100])

from scipy.stats import ttest_ind, pearsonr, f_oneway

# ---------- HYPOTHESIS TESTS ----------

# H1: Cardio burns more calories than Yoga
cardio = df[df['Workout_Type'] == 'Cardio']['Calories_Burned']
yoga = df[df['Workout_Type'] == 'Yoga']['Calories_Burned']

t_stat, p_val = ttest_ind(cardio, yoga, equal_var=False)
print(f"\n[H1] T-test - Cardio vs Yoga (Calories Burned):\nT-statistic = {t_stat:.2f}, P-value = {p_val:.4f}")

sns.boxplot(x='Workout_Type', y='Calories_Burned', data=df[df['Workout_Type'].isin(['Cardio', 'Yoga'])])
plt.title('Calories Burned: Cardio vs Yoga')
plt.show()


# H2: Steps and Calories Burned are positively correlated
corr, p_value = pearsonr(df['Steps'], df['Calories_Burned'])
print(f"\n[H2] Pearson Correlation - Steps vs Calories Burned:\nCorrelation = {corr:.2f}, P-value = {p_value:.4f}")

sns.regplot(x='Steps', y='Calories_Burned', data=df)
plt.title('Steps vs Calories Burned')
plt.show()


# H3: Average heart rate varies by workout type (ANOVA)
groups = [group['Heart_Rate_avg'].values for name, group in df.groupby('Workout_Type')]
f_stat, p_val = f_oneway(*groups)
print(f"\n[H3] ANOVA - Heart Rate by Workout Type:\nF-statistic = {f_stat:.2f}, P-value = {p_val:.4f}")

sns.boxplot(x='Workout_Type', y='Heart_Rate_avg', data=df)
plt.title('Heart Rate Across Workout Types')
plt.show()


