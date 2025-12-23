from gui.trading_app import TradingApp
import ttkbootstrap as ttk
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def main():
    root = ttk.Window(themename="cyborg")
    TradingApp(root)
    root.mainloop()
    root.state('zoomed')

if __name__ == "__main__":
    main()
