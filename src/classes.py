import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):

        self.df = pd.read_csv(filepath)

        self.ph_min = ph_lims[0]
        self.ph_max = ph_lims[1]

        self.temperature_min = temperature_lims[0]
        self.temperature_max = temperature_lims[1]

    def extract_batch(self, batch_id):

        df_batch = self.df[self.df["batch_id"] == batch_id]

        return df_batch

    def optimal_ph_mask(self, df_batch):

        ph_mask = (
            (df_batch["pH"] >= self.ph_min)
            & (df_batch["pH"] <= self.ph_max)
        )

        return ph_mask

    def optimal_temperature_mask(self, df_batch):

        temperature_mask = (
            (df_batch["temperature_C"] >= self.temperature_min)
            & (df_batch["temperature_C"] <= self.temperature_max)
        )
        return temperature_mask

    def get_n_batches(self):

        n_batches = self.df["batch_id"].nunique()

        return n_batches

    def export_dashboard(self, batch_id, filepath):

        df_batch = self.extract_batch(batch_id)

        ph_mask = self.optimal_ph_mask(df_batch)
        temperature_mask = self.optimal_temperature_mask(df_batch)

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # 1- Glucose, biomass, and product concentrations vs time.
        # A different color and marker should be used for each substance. OK

        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_glucose_g_L^-1"],
            label="Glucose",
            marker="o"
        )

        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_biomass_g_L^-1"],
            label="Biomass",
            marker="^"
        )

        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_product_g_L^-1"],
            label="Product",
            marker="s"
        )

        axes[0, 0].set_xlabel("Time [h]")
        axes[0, 0].set_ylabel("Concentration [g/L]")
        axes[0, 0].legend()

        # 2- Temperature vs time.
        #             - Measurements within the acceptable temperature range OK
        #               should be displayed as green circles. OK
        #             - Measurements outside the acceptable temperature range OK
        #               should be displayed as red X markers. OK

        axes[0, 1].scatter(
            df_batch.loc[temperature_mask, "time_h"],
            df_batch.loc[temperature_mask, "temperature_C"],
            color="green",
            marker="o",
            label="Optimal"
        )

        axes[0, 1].scatter(
            df_batch.loc[~temperature_mask, "time_h"],
            df_batch.loc[~temperature_mask, "temperature_C"],
            color="red",
            marker="X",
            label="Sub-Optimal"
        )

        axes[0, 1].set_xlabel("Time [h]")
        axes[0, 1].set_ylabel("Temperature [°C]")
        axes[0, 1].legend()

        # 3- pH vs time.
        #             - Measurements within the acceptable pH range OK
        #               should be displayed as green circles OK
        #             - Measurements outside the acceptable pH range OK
        #               should be displayed as red X markers. OK
        axes[1, 0].scatter(
            df_batch.loc[ph_mask, "time_h"],
            df_batch.loc[ph_mask, "pH"],
            color="green",
            marker="o",
            label="Optimal"
        )

        axes[1, 0].scatter(
            df_batch.loc[~ph_mask, "time_h"],
            df_batch.loc[~ph_mask, "pH"],
            color="red",
            marker="X",
            label="Sub-Optimal"
        )

        axes[1, 0].set_xlabel("Time [h]")
        axes[1, 0].set_ylabel("pH")
        axes[1, 0].legend()

        #4- dissolved oxygen

        axes[1, 1].scatter(
            df_batch["time_h"],
            df_batch["DO_percent"]
        )

        axes[1, 1].set_xlabel("Time [h]")
        axes[1, 1].set_ylabel("Dissolved Oxygen [%]")

# 6 hour tick spacing

        for ax in axes.flat:
            ax.xaxis.set_major_locator(MultipleLocator(6))

        plt.tight_layout()
        fig.savefig(filepath)
        plt.close(fig)

        # """
        #         Additional Requirements
        #         -----------------------
        #         - Use scatter plots.
        #         - Add x-axis and y-axis labels.
        #         - Add legends where appropriate.
        #         - Apply consistent formatting across all subplots unless
        #           indicated otherwise.
        #         - Apply a tick spacing of 6 h on the x-axis for all subplots.
        #         - Save the figure to the provided filepath.
        #         - Close the figure after saving.
        #         """


    def export_summary(self, filepath):

        summary_rows = []

        for batch_id in range(1, self.get_n_batches() + 1):
            df_batch = self.extract_batch(batch_id)

            ph_percent = round(
                self.optimal_ph_mask(df_batch).mean() * 100,
                2
            )

            temperature_percent = round(
                self.optimal_temperature_mask(df_batch).mean() * 100,
                2
            )

            final_product = df_batch["C_product_g_L^-1"].iloc[-1]

            summary_rows.append({
                "batch_id": batch_id,
                "ph_optimal_percent": ph_percent,
                "temperature_optimal_percent": temperature_percent,
                "C_product_g_L^-1_final": final_product
            })

        df_summary = pd.DataFrame(summary_rows)

        df_summary.to_csv(filepath, index=False)