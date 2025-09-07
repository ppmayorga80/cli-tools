import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_summary(df):
    df['day'] = df['sign_in'].dt.day
    df['hour'] = df['sign_in'].dt.hour

    summary = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
    summary = summary.sort_index().sort_index(axis=1)

    return summary

def align_date_range(df1, df2):
    df1['sign_in'] = pd.to_datetime(df1['sign_in'])
    df2['sign_in'] = pd.to_datetime(df2['sign_in'])

    start_date = max(df1['sign_in'].min(), df2['sign_in'].min())
    end_date = min(df1['sign_in'].max(), df2['sign_in'].max())

    df1_filtered = df1[(df1['sign_in'] >= start_date) & (df1['sign_in'] <= end_date)].copy()
    df2_filtered = df2[(df2['sign_in'] >= start_date) & (df2['sign_in'] <= end_date)].copy()

    return df1_filtered, df2_filtered

def plot_all(df_cli, df_usr):
    # Align both to common date range
    df_cli, df_usr = align_date_range(df_cli, df_usr)
    df_merged = pd.concat([df_cli, df_usr], ignore_index=True)

    # Prepare summaries
    summary_cli = prepare_summary(df_cli)
    summary_usr = prepare_summary(df_usr)
    summary_merged = prepare_summary(df_merged)

    # Unified color scale
    combined = pd.concat([
        summary_cli.stack(),
        summary_usr.stack(),
        summary_merged.stack()
    ])
    v_min = combined.min()
    v_max = combined.max()

    # Plotting
    fig, axes = plt.subplots(1, 3, figsize=(30, 8))  # 1 row, 3 columns

    sns.heatmap(summary_cli, cmap='viridis', linewidths=0.5, linecolor='gray',
                ax=axes[0], vmin=v_min, vmax=v_max)
    axes[0].set_title('Sign-ins (Clients)', fontsize=14)
    axes[0].set_xlabel('Hour of Day')
    axes[0].set_ylabel('Day of Month')
    axes[0].tick_params(axis='x', rotation=0)
    axes[0].tick_params(axis='y', rotation=0)

    sns.heatmap(summary_usr, cmap='viridis', linewidths=0.5, linecolor='gray',
                ax=axes[1], vmin=v_min, vmax=v_max)
    axes[1].set_title('Sign-ins (Users)', fontsize=14)
    axes[1].set_xlabel('Hour of Day')
    axes[1].set_ylabel('Day of Month')
    axes[1].tick_params(axis='x', rotation=0)
    axes[1].tick_params(axis='y', rotation=0)

    sns.heatmap(summary_merged, cmap='viridis', linewidths=0.5, linecolor='gray',
                ax=axes[2], vmin=v_min, vmax=v_max)
    axes[2].set_title('Sign-ins (Clients + Users)', fontsize=14)
    axes[2].set_xlabel('Hour of Day')
    axes[2].set_ylabel('Day of Month')
    axes[2].tick_params(axis='x', rotation=0)
    axes[2].tick_params(axis='y', rotation=0)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    df1 = pd.read_csv("/Users/pedro/Downloads/dt-clients.csv")
    df2 = pd.read_csv("/Users/pedro/Downloads/dt-users.csv")

    plot_all(df_cli=df1, df_usr=df2)
