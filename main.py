import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

db_url = 'postgresql+psycopg2://postgres:postgres@localhost:5432/shop_analytics'

engine = create_engine(db_url)

query = """
    SELECT sale_date, total_amount
    FROM sales
    ORDER BY sale_date ASC;
"""

df = pd.read_sql(query, engine)

df['sale_date'] = pd.to_datetime(df['sale_date'])

df.set_index('sale_date', inplace=True)

daily_sales = df['total_amount'].resample('D').sum().fillna(0)

print("--- 1. Дневная выручка (последние 5 дней) ---")
print(daily_sales.tail(5))
print("\n")

cumulative_sales = daily_sales.cumsum()

print("--- 2. Накопительная выручка (последние 5 дней) ---")
print(cumulative_sales.tail(5))
print("\n")

rolling_avg_7d = daily_sales.rolling(window=7).mean()

print("--- 3. Скользящее среднее за 7 дней (последние 5 дней) ---")
print(rolling_avg_7d.tail(5))
print("\n")

analytics_df = pd.DataFrame({
    'Дневная выручка': daily_sales,
    'Накопительная выручка': cumulative_sales,
    'Тренд (7 дней)': rolling_avg_7d
})

analytics_df = analytics_df.round(2)

print("--- ИТОГОВАЯ ТАБЛИЦА ДИНАМИКА (фрагмент) ---")
print(analytics_df.tail(10))

plt.style.use('seaborn-v0_8-darkgrid')

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

axes[0].bar(daily_sales.index, daily_sales.values,
            color='cornflowerblue', alpha=0.5, label='Дневная выручка')
axes[0].plot(rolling_avg_7d.index, rolling_avg_7d.values,
             color='crimson', linewidth=2.2, label='Тренд (7 дней)')
axes[0].set_title('Динамика продаж и скользящее среднее (Тренд)')
axes[0].set_ylabel('Сумма')
axes[0].legend(loc='upper left')

axes[1].plot(cumulative_sales.index, cumulative_sales.values,
             color='seagreen', linewidth=2, label='Накопительный итог')
axes[1].fill_between(cumulative_sales.index, cumulative_sales.values,
                     color='seagreen', alpha=0.2)
axes[1].set_title('Накопительная выручка за весь период')
axes[1].set_ylabel('Общая сумма')
axes[1].set_xlabel('Дата')
axes[1].legend(loc='upper left')

plt.tight_layout()
plt.savefig('sales_analytics.png', dpi=150)

top_products_query = """
    SELECT p.name AS product_name,
           SUM(s.total_amount) AS revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.name
    ORDER BY revenue DESC
    LIMIT 5;
"""

top_products = pd.read_sql(top_products_query, engine)

print("\n--- 4. ТОП-5 товаров по выручке ---")
print(top_products)

def format_money(value: float, with_symbol: bool = True) -> str:
    symbol = ' ₸' if with_symbol else ''
    if value >= 1_000_000_000:
        return f'{value / 1_000_000_000:.2f} млрд{symbol}'
    if value >= 1_000_000:
        return f'{value / 1_000_000:.1f} млн{symbol}'
    if value >= 1_000:
        return f'{value / 1_000:.1f} тыс{symbol}'
    return f'{value:.0f}{symbol}'


top_products = top_products.sort_values('revenue', ascending=False).reset_index(drop=True)
total_revenue_top5 = top_products['revenue'].sum()

top_products['label'] = [
    f'#{i + 1}  {name}' for i, name in enumerate(top_products['product_name'])
]

plot_df = top_products.iloc[::-1].reset_index(drop=True)

colors = plt.cm.viridis([0.15, 0.30, 0.50, 0.70, 0.88])

fig2, ax = plt.subplots(figsize=(13, 6.5))
fig2.patch.set_facecolor('white')
ax.set_facecolor('#f7f7fb')

bars = ax.barh(plot_df['label'], plot_df['revenue'],
               color=colors, edgecolor='white', linewidth=1.2, height=0.65)

max_revenue = plot_df['revenue'].max()

for bar, value in zip(bars, plot_df['revenue']):
    share = value / total_revenue_top5 * 100
    ax.text(bar.get_width() + max_revenue * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{format_money(value)}   ({share:.1f}%)',
            va='center', ha='left',
            fontsize=11, color='#222')

ax.set_title('ТОП-5 товаров по выручке',
             fontsize=16, fontweight='bold', pad=18, loc='left')
ax.text(0, 1.02,
        f'Суммарно у лидеров: {format_money(total_revenue_top5)}',
        transform=ax.transAxes, fontsize=10, color='#666')

ax.set_xlabel('Выручка, ₸', fontsize=11, color='#555')
ax.set_ylabel('')
ax.tick_params(axis='y', labelsize=11)
ax.set_xlim(0, max_revenue * 1.28)

ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.grid(axis='y', visible=False)
ax.xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: format_money(x, with_symbol=False) if x > 0 else '0')
)

for spine in ('top', 'right', 'left'):
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_color('#cccccc')

plt.tight_layout()
plt.savefig('top_products.png', dpi=150, bbox_inches='tight')
plt.show()