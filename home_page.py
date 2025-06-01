import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from violation_log_window import ViolationLogWindow  # your log viewer

# Constants
FINED_CSV = 'fined.csv'
towns = ['All','Harare','Bulawayo','Mutare','Gweru','Kadoma','Chinhoyi','Bindura',
         'Marondera','Norton','Masvingo','Chiredzi','Mutoko','Chipinge','Rusape']


class HomePage(ttk.Frame):
    """
    Dashboard frame with 2×2 layout:
      - Top-left: Pie chart (All) or monthly bar (City)
      - Top-right: Time series (All weekly multi-city or City hourly)
      - Bottom-left: Doughnut (Violations vs Passed)
      - Bottom-right: Bar (All monthly) or Scatter (City weekly)
      - Controls: Location, date range, Refresh, Export PNG, Violation Logs
    """
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self._build_ui()
        self._plot_all()

    def _build_ui(self):
        ctrl = ttk.Frame(self)
        ctrl.pack(fill=tk.X, pady=5, padx=10)

        # Filters
        ttk.Label(ctrl, text='Location:').pack(side=tk.LEFT, padx=5)
        self.loc_var = tk.StringVar(value='All')
        self.loc_cb = ttk.Combobox(ctrl, values=towns, state='readonly', textvariable=self.loc_var)
        self.loc_cb.pack(side=tk.LEFT)
        self.loc_cb.bind('<<ComboboxSelected>>', lambda e: self._plot_all())

        ttk.Label(ctrl, text='Start (YYYY-MM-DD):').pack(side=tk.LEFT, padx=5)
        self.start_var = tk.StringVar()
        ttk.Entry(ctrl, width=12, textvariable=self.start_var).pack(side=tk.LEFT)

        ttk.Label(ctrl, text='End (YYYY-MM-DD):').pack(side=tk.LEFT, padx=5)
        self.end_var = tk.StringVar()
        ttk.Entry(ctrl, width=12, textvariable=self.end_var).pack(side=tk.LEFT)

        # Action buttons
        ttk.Button(ctrl, text='Refresh', command=self._plot_all).pack(side=tk.RIGHT, padx=5)
        ttk.Button(ctrl, text='Export PNG', command=self._export_png).pack(side=tk.RIGHT, padx=5)
        ttk.Button(ctrl, text='Violation Logs', command=lambda: ViolationLogWindow(self)).pack(side=tk.RIGHT, padx=5)

        # Matplotlib figure
        self.fig = Figure(figsize=(10,6), dpi=100)
        self.ax_pie  = self.fig.add_subplot(221)
        self.ax_ts   = self.fig.add_subplot(222)
        self.ax_heat = self.fig.add_subplot(223)
        self.ax_bar  = self.fig.add_subplot(224)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _export_png(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG Image','*.png')]
        )
        if path:
            self.fig.savefig(path)
            messagebox.showinfo('Export', f'Dashboard saved to\n{path}')

    def _load_data(self):
        if not os.path.exists(FINED_CSV):
            return pd.DataFrame()
        df = pd.read_csv(FINED_CSV, parse_dates=['timestamp'])
        loc = self.loc_var.get()
        if loc != 'All':
            df = df[df['location'] == loc]
        if self.start_var.get().strip():
            df = df[df['timestamp'] >= self.start_var.get().strip()]
        if self.end_var.get().strip():
            df = df[df['timestamp'] <= self.end_var.get().strip()]
        return df

    def _plot_all(self):
        df = self._load_data()
        for ax in (self.ax_pie, self.ax_ts, self.ax_heat, self.ax_bar):
            ax.clear()

        if df.empty:
            for ax in (self.ax_pie, self.ax_ts, self.ax_heat, self.ax_bar):
                ax.text(0.5,0.5,'No Data', ha='center', va='center')
            self.canvas.draw()
            return

        loc = self.loc_var.get()

        # Top-left
        if loc == 'All':
            by_city = df.groupby('location')['violations'].sum()
            by_city.plot.pie(ax=self.ax_pie, autopct='%1.1f%%', legend=False)
            self.ax_pie.set_title('Violations by City')
        else:
            monthly = df.set_index('timestamp')['violations'].resample('M').sum()
            self.ax_pie.bar(monthly.index.strftime('%b %Y'), monthly.values, color='teal')
            self.ax_pie.set_title(f'Monthly Violations – {loc}')
            self.ax_pie.tick_params(axis='x', rotation=55)

        # Top-right
        if loc == 'All':
            ts = (df.set_index('timestamp')
                    .groupby('location')['violations']
                    .resample('W').sum()
                    .unstack(0).fillna(0))
            for city in ts.columns:
                self.ax_ts.plot(ts.index, ts[city], marker='o', label=city)
            self.ax_ts.legend(fontsize='small', loc='upper left')
            self.ax_ts.set_title('Weekly Violations by City')
        else:
            hourly = df.set_index('timestamp')['violations'].resample('H').sum()
            self.ax_ts.plot(hourly.index, hourly.values, marker='.', linestyle='-')
            self.ax_ts.set_title(f'Hourly Violations – {loc}')
        self.ax_ts.tick_params(axis='x', rotation=45)

        # Bottom-left doughnut
        vp = df['violations'].sum()
        cp = df['cars_passed'].sum()
        sizes = [vp, max(cp-vp,0)]
        wedges, texts, autotexts = self.ax_heat.pie(
            sizes,
            labels=['Violations','Non-Violations'],
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.4)
        )
        subtitle = f'{loc}: Violations vs Passed' if loc!='All' else 'Overall: Violations vs Passed'
        self.ax_heat.set_title(subtitle)

        # Bottom-right
        if loc == 'All':
            monthly_all = df.set_index('timestamp')['violations'].resample('M').sum()
            self.ax_bar.bar(monthly_all.index.strftime('%b %Y'), monthly_all.values, color='orange')
            self.ax_bar.set_title('Monthly Violations')
        else:
            weekly = df.set_index('timestamp')['violations'].resample('W').sum()
            self.ax_bar.scatter(weekly.index, weekly.values, c='green')
            self.ax_bar.set_title(f'Weekly Violations – {loc}')
        self.ax_bar.tick_params(axis='x', rotation=45)

        self.fig.tight_layout()
        self.canvas.draw()
