"""Redraw the supplied entity P5-P95 summaries without any model execution."""
from pathlib import Path
import argparse
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parent
    with (root / 'figure2b/figure2b_distribution_stats.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    lookup = {(r['dataset'], r['condition']): r for r in rows}
    assert len(lookup) == 9 and all(int(r['seed']) == 42 and float(r['eta']) == .30 for r in rows)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    fig, ax = plt.subplots(figsize=(7.2, 3.05))
    fig.subplots_adjust(left=.085, right=.995, bottom=.22, top=.84)
    ticks, labels = [], []
    for di, dataset in enumerate(['MKG-Y', 'MKG-W', 'DB15K']):
        for ci, condition in enumerate(['Clean', 'Hard', 'Random']):
            center = di * 4 + [-.82, 0, .82][ci]
            ticks.append(center)
            labels.append(condition)
            row = lookup[dataset, condition]
            for state, shift, color, legend in [('before', -.145, '#A7ADB5', 'Before calibration'), ('after', .145, '#0072B2', 'After calibration')]:
                mean, low, high = [float(row[state + '_' + stat]) for stat in ['mean', 'p5', 'p95']]
                assert low <= mean <= high
                ax.bar(center + shift, mean, width=.29, color=color, edgecolor='white', label=legend if di == ci == 0 else None, zorder=2)
                ax.errorbar(center + shift, mean, yerr=np.array([[mean-low], [high-mean]]), fmt='none', ecolor='#292E34', elinewidth=.85, capsize=2, capthick=.85, zorder=3)
        ax.text(di*4, -.15, dataset, transform=ax.get_xaxis_transform(), ha='center', va='top', fontweight='bold', fontsize=7.5)
    ax.set_xticks(ticks, labels)
    ax.set_ylabel(r'Mean visual weight $\alpha_v$')
    ax.set_ylim(0, max(.60, max(float(r[s + '_p95']) for r in rows for s in ['before', 'after']) + .025))
    ax.set_title('(b) Reliability-calibrated visual contribution', loc='left', pad=23)
    ax.grid(axis='y', color='#D7DBE0', linewidth=.6)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc='lower center', bbox_to_anchor=(.5, 1.005), fontsize=7)
    fig.text(.54, .012, 'Bars: entity mean. Whiskers: entity P5-P95 (not a confidence interval).', ha='center', fontsize=6.5)
    for suffix in ['png', 'pdf', 'svg']:
        fig.savefig(out / ('Figure2b_redrawn.' + suffix), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print('Saved independent redraws to ' + str(out))

if __name__ == '__main__':
    main()
