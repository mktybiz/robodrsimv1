import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# ----------------------------------------------------
# Streamlit 基本設定
# ----------------------------------------------------
st.set_page_config(page_title="ビジネスモデル 収益・支出試算", layout="wide")
st.title("ビジネスモデル シミュレーション")

st.sidebar.header("シミュレーションパラメータ")

# ----------------------------------------------------
# 期間パラメータ（★シミュレーション年数）
# ----------------------------------------------------
years = st.sidebar.slider("シミュレーション年数（年）", min_value=1, max_value=10, value=7, step=1)
MONTHS = years * 12

# ----------------------------------------------------
# アプリ関連パラメータ
# ----------------------------------------------------
st.sidebar.caption(f"プラットフォーマー手数料＝15%")
monthly_fee = st.sidebar.number_input("アプリ月額料金（円）", min_value=0, value=300, step=10)

# ----------------------------------------------------
# ロボット販売・手数料関連
# ----------------------------------------------------
#units_per_event = st.sidebar.number_input("イベントあたり販売台数（台）", min_value=0, value=2, step=1)
attendees_per_event = st.sidebar.number_input("イベントあたり集客数（人）", min_value=0, value=50, step=1)

# ----------------------------------------------------
# 販売会社イベント
# ----------------------------------------------------
events_per_company_per_month = st.sidebar.number_input("1社あたり月間イベント数（回）", min_value=0, value=2, step=1)

# ----------------------------------------------------
# 既存ユーザー向けアプリ課金
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption(f"ロボット保有顧客の月当たり新規課金登録者")
robot_uio_users_per_month = st.sidebar.number_input("新規課金登録者数（人）", min_value=0, value=0, step=1)


# ----------------------------------------------------
# タブ定義
# ----------------------------------------------------
tab_summary, tab_graphs, tab_settings  = st.tabs(["📋 サマリー", "📊 グラフ", "⚙ 設定"])


with tab_settings:
    # ----------------------------------------------------
    # 収入パラメータ（メイン領域）
    # ----------------------------------------------------
    st.header("収入パラメータ設定")
    st.subheader("アプリ課金")
    col = st.columns(2)
    with col[0]:
        free_months = st.number_input("無料期間（月）", min_value=0, max_value=24, value=3, step=1)
    with col[1]:
        churn_rate = st.slider("月間解約率（%）", min_value=0.0, max_value=50.0, value=3.0, step=0.5) / 100.0

    st.subheader("ロボット販売収益")

    # ロボット種類数を指定
    num_robot_types = st.number_input(
        "ロボット種類数",
        min_value=1,
        max_value=10,
        value=1,
        step=1,
    )
    num_robot_types = int(num_robot_types)

    # 種類ごとの設定を格納する配列
    robot_names = []
    robot_prices = []
    commission_rates = []
    purchase_rates =[]

    for i in range(num_robot_types):
        with st.expander(f"ロボットNo{i + 1} の設定", expanded=(i == 0)):
            col = st.columns(2)
            with col[0]:
                name = st.text_input(
                    f"ロボット名",
                    value=f"No{i + 1}",
                    key=f"robot_name_{i}",
                )
                price = st.number_input(
                    f"小売価格（円）",
                    min_value=0,
                    value=230_000,
                    step=1_000,
                    key=f"robot_price_{i}",
                )
            with col[1]:
                commission_rate = st.slider(
                    f"販売手数料率（%）",
                    min_value=0.0,
                    max_value=25.0,
                    value=10.0,
                    step=1.0,
                    key=f"commission_rate_{i}",
                ) / 100.0
                purchase_rate = st.slider(
                    f"購入率（%）",
                    min_value=0.0,
                    max_value=10.0,
                    value=3.0,
                    step=0.1,
                    key=f"purchase_rate_{i}",
                ) / 100.0

            robot_names.append(name)
            robot_prices.append(price)
            commission_rates.append(commission_rate)
            purchase_rates.append(purchase_rate)

    # ----------------------------------------------------
    # 販売会社（★毎月の増加数をパラメータ化）
    # ----------------------------------------------------
    st.subheader("販売会社（増加数）")
    col = st.columns(2)
    with col[0]:
        initial_companies = st.number_input("開始販売会社数", min_value=1, value=1, step=1)
        max_companies = st.number_input("販売会社数の上限（社）", min_value=1, value=100, step=1)
    with col[1]:
        fixed_months_before_growth = st.number_input("初期実証期間", min_value=1, value=6, step=1)
        company_growth_per_month = st.number_input(
        "販売会社数の毎月の増加数（社／月）", min_value=0, value=2, step=1
        )
    st.caption(f"販売会社数：1社（{fixed_months_before_growth}ヶ月）→ 以降は毎月の増加数だけ増加 → 上限に達したら停止")

    st.markdown("---")


    # ----------------------------------------------------
    # 支出パラメータ（メイン領域）
    # ----------------------------------------------------
    st.header("支出パラメータ設定")
    st.subheader("アプリ開発・不具合修正")
    col = st.columns(2)
    with col[0]:
        android_dev_initial = st.number_input("Android 初期開発費（万円）",
                                              min_value=0, value=450, step=10) * 10000
        ios_dev_initial = st.number_input("iPhone 初期開発費（万円）",
                                          min_value=0, value=650, step=10) * 10000
        ios_dev_month = st.number_input("iPhone開発時期", min_value=0, value=12, step=1)
    with col[1]:
        android_bugfix_cost = st.number_input("Android 不具合修正費用（万円）",
                                              min_value=0, value=100, step=10) * 10000
        ios_bugfix_cost = st.number_input("iPhone 不具合修正費用（万円）",
                                          min_value=0, value=100, step=10) * 10000
        bugfix_cycle_months = st.number_input("不具合修正リリース周期（ヶ月）", min_value=1, value=6, step=1)

    st.subheader("クラウドシステム")
    col = st.columns(2)
    with col[0]:
        cloud_initial = st.number_input("クラウド初期構築費用（万円）", min_value=0, value=350, step=10) * 10000
        cloud_bugfix_cost = st.number_input("クラウド不具合修正費用（万円）", min_value=0, value=100, step=10) * 10000
        num_thresholds = st.number_input("クラウド増強回数", min_value=0, value=4, step=1)
    with col[1]:
        aws_cost_per_user_month = st.number_input("AWS費用（有料会員あたり月額・円）", min_value=0, value=50, step=5)

    # デフォルト値とステップを配列で定義
    default_threshold_values = [300, 1000, 3000, 10000]
    default_threshold_steps = [100, 100, 500, 1000]
    default_scale_cost_values = [100, 150, 200, 300]

    # 足りない要素を自動で補完（最後の値を繰り返し利用）
    def expand_list(lst, target_len):
        return lst + [lst[-1]] * (target_len - len(lst))

    default_threshold_values = expand_list(default_threshold_values, num_thresholds)
    default_threshold_steps = expand_list(default_threshold_steps, num_thresholds)
    default_scale_cost_values = expand_list(default_scale_cost_values, num_thresholds)

    # 結果格納用の配列
    cloud_scale_thresholds = []
    cloud_scale_costs = []

    col9, col10 = st.columns(2)
    with col9:
        for i in range(num_thresholds):
            threshold = st.number_input(
                f"クラウド増強閾値 No{i+1}（有料会員数）",
                min_value=0,
                value=default_threshold_values[i],
                step=default_threshold_steps[i],
            )
            cloud_scale_thresholds.append(threshold)
    with col10:
        for i in range(num_thresholds):
            cost = st.number_input(
                f"クラウド増強費用 No{i+1}（万円）",
                min_value=0,
                value=default_scale_cost_values[i],
                step=10
            ) * 10000  # 円換算
            cloud_scale_costs.append(cost)

    st.markdown("---")
    st.subheader("販売店向けロボット・販売ツール")
    col11, col12 = st.columns(2)
    with col11:
        robot_unit_cost = st.number_input("ロボット1式費用（円）", min_value=0, value=sum(robot_prices), step=1000)
        sales_tool_cost_per_shop = st.number_input("販売ツール一式費用／社（万円）", min_value=0, value=20, step=1) * 10000
    with col12:
        robots_per_shop = st.number_input("販売店あたりロボット台数（台）", min_value=0, value=4, step=1)

    st.subheader("カスタマーサポート")
    colmk5, colmk6 = st.columns(2)
    with colmk5:
        cs_cost_per_user_month = st.number_input(
            "CS費用（有料会員あたり月額・円）", min_value=0, value=10, step=10)


    st.subheader("事業体人件費")
    col13, col14 = st.columns(2)
    with col13:
        base_fte = st.number_input("初期事業体要員（人）", min_value=0.0, value=1.0, step=0.1)
        fte_cost_per_month = st.number_input("人月当たり人件費（万円）", min_value=0, value=120, step=10) * 10000
    with col14:
        base_users = st.number_input("増員なしの上限（有料会員数）", min_value=0, value=2000, step=100)
        fte_increment_users = st.number_input("増員基準（有料会員数）", min_value=1, value=4000, step=100)
        fte_increment = st.number_input("追加人員（人）", min_value=0.0, value=0.5, step=0.1)


# ----------------------------------------------------
# 配列の準備（★MONTHS に応じて動的生成）
# ----------------------------------------------------
contract_companies = [0] * MONTHS
events_per_month = [0] * MONTHS
new_users = [0] * MONTHS
trial_starts = [0] * MONTHS
paying_users = [0.0] * MONTHS
app_revenue = [0.0] * MONTHS
commission_revenue = [0.0] * MONTHS
total_revenue = [0.0] * MONTHS

# ----------------------------------------------------
# 月次シミュレーション（収益）
# ----------------------------------------------------
# ループの前で、ロボット種別ごとの販売台数配列を用意しておく
robot_sales_by_type = [[0] * MONTHS for _ in range(num_robot_types)]

for m in range(MONTHS):

    # 契約販売会社数の推移
    if m < fixed_months_before_growth:
        companies = initial_companies
    else:
        months_since_growth = m - fixed_months_before_growth + 1
        companies = initial_companies + company_growth_per_month * months_since_growth
        companies = min(companies, max_companies)

    contract_companies[m] = companies

    # イベント数
    events = companies * events_per_company_per_month
    events_per_month[m] = events



    # --- 複数種類のロボットに対応した計算 ---

    total_robots_sold = 0
    total_commission = 0.0

    for i in range(num_robot_types):
        # 種類ごとの販売台数（イベント数 × 集客数　×　種別ごとの購入率）
        robots_sold_i = int(events *  attendees_per_event * purchase_rates[i])
        robot_sales_by_type[i][m] = robots_sold_i

        # 全種類の販売台数を合計（= 新規ユーザー数）
        total_robots_sold += robots_sold_i

        # 種類ごとの販売手数料
        commission_i = robots_sold_i * robot_prices[i] * commission_rates[i]
        total_commission += commission_i

    # 新規ユーザー（全ロボット種別の合計販売台数）
    new_users[m] = total_robots_sold
    trial_starts[m] = total_robots_sold + robot_uio_users_per_month

    # 販売手数料収入（全ロボット種別の合計）
    commission_revenue[m] = total_commission

    # 有料会員数
    prev = paying_users[m - 1] if m > 0 else 0
    churn = prev * churn_rate
    remaining = prev - churn

    # 無料期間後に課金開始
    conversions = trial_starts[m - free_months] if m >= free_months else 0
    paying_users[m] = remaining + conversions

    # アプリ収入
    app_revenue[m] = paying_users[m] * monthly_fee * 0.85

    # 総売上
    total_revenue[m] = app_revenue[m] + commission_revenue[m]

# ----------------------------------------------------
# ★ 支出シミュレーション（有料会員数ベース）
# ----------------------------------------------------

# 「ユーザー数に応じた費用」は有料会員数を使う
users_for_cost = paying_users  # ここがポイント

# 月次支出項目の配列
cost_app_android_initial = [0] * MONTHS
cost_app_ios_initial = [0] * MONTHS
cost_app_android_bugfix = [0] * MONTHS
cost_app_ios_bugfix = [0] * MONTHS

cost_cloud_initial_arr = [0] * MONTHS
cost_cloud_aws = [0] * MONTHS
cost_cloud_bugfix_arr = [0] * MONTHS
cost_cloud_scale = [0] * MONTHS

cost_shop_acquisition = [0] * MONTHS
cost_customer_support = [0] * MONTHS

potstill_fte = [0.0] * MONTHS
cost_potstill_salary = [0.0] * MONTHS

# 初期費用（アプリ・クラウド）
if MONTHS > 0:
    cost_app_android_initial[0] = android_dev_initial
    cost_app_ios_initial[ios_dev_month] = ios_dev_initial
    cost_cloud_initial_arr[0] = cloud_initial

# 不具合修正：bugfix_cycle_months ごと
for m in range(MONTHS):
    if m % bugfix_cycle_months == 0:
        if m < 1:
            cost_app_android_bugfix[m] = 0
            cost_cloud_bugfix_arr[m] = 0
        else:
            cost_app_android_bugfix[m] = android_bugfix_cost
            cost_cloud_bugfix_arr[m] = cloud_bugfix_cost
        if m < ios_dev_month + 1:
            cost_app_ios_bugfix[m] = 0
        else:
            cost_app_ios_bugfix[m] = ios_bugfix_cost


# AWS費用・CS費用（有料会員数に比例）
for m in range(MONTHS):
    users = users_for_cost[m]
    cost_cloud_aws[m] = users * aws_cost_per_user_month
    cost_customer_support[m] = users * cs_cost_per_user_month

# クラウド増強費用（有料会員数が閾値を初めて超えた月に1回だけ）
threshold_flags = [False] * len(cloud_scale_thresholds)
for m in range(MONTHS):
    users_prev = users_for_cost[m - 1] if m > 0 else 0
    users_now = users_for_cost[m]
    for i, th in enumerate(cloud_scale_thresholds):
        if threshold_flags[i]:
            continue
        if users_prev < th <= users_now:
            cost_cloud_scale[m] += cloud_scale_costs[i]
            threshold_flags[i] = True

# 販売店ごとのロボット・ツール費用（新規販売会社数×一式費用）
new_companies = [0] * MONTHS
for m in range(MONTHS):
    if m == 0:
        new_companies[m] = contract_companies[m]
    else:
        diff = contract_companies[m] - contract_companies[m - 1]
        new_companies[m] = diff if diff > 0 else 0

per_shop_acquisition_cost = robots_per_shop * robot_unit_cost + sales_tool_cost_per_shop
for m in range(MONTHS):
    cost_shop_acquisition[m] = new_companies[m] * per_shop_acquisition_cost

# 事業体人件費（有料会員数ベース）
for m in range(MONTHS):
    users = users_for_cost[m]
    users_over_base = max(0, users - base_users)
    increments = math.ceil(users_over_base / fte_increment_users) if users_over_base > 0 else 0
    fte = base_fte + increments * fte_increment
    potstill_fte[m] = fte
    cost_potstill_salary[m] = fte * fte_cost_per_month

# 月次総支出
total_expense = [0.0] * MONTHS
for m in range(MONTHS):
    total_expense[m] = (
        cost_app_android_initial[m]
        + cost_app_ios_initial[m]
        + cost_app_android_bugfix[m]
        + cost_app_ios_bugfix[m]
        + cost_cloud_initial_arr[m]
        + cost_cloud_aws[m]
        + cost_cloud_bugfix_arr[m]
        + cost_cloud_scale[m]
        + cost_shop_acquisition[m]
        + cost_customer_support[m]
        + cost_potstill_salary[m]
    )

# 月次利益（売上－支出）
profit = [total_revenue[m] - total_expense[m] for m in range(MONTHS)]

# ----------------------------------------------------
# 年次集計（★years に応じて可変）
# ----------------------------------------------------
annual_total = []
annual_app = []
annual_commission = []
annual_robot_sales = []
annual_expense = []
annual_profit = []

for y in range(years):
    start = y * 12
    end = min((y + 1) * 12, MONTHS)

    annual_total.append(sum(total_revenue[start:end]))
    annual_app.append(sum(app_revenue[start:end]))
    annual_commission.append(sum(commission_revenue[start:end]))
    annual_robot_sales.append(sum(new_users[start:end]))
    annual_expense.append(sum(total_expense[start:end]))
    annual_profit.append(sum(profit[start:end]))

# 年間ロボット販売台数（種類別）
annual_robot_sales_by_type = [
    [0] * years for _ in range(num_robot_types)
]

for i in range(num_robot_types):
    for y in range(years):
        start = y * 12
        end = min((y + 1) * 12, MONTHS)
        annual_robot_sales_by_type[i][y] = sum(robot_sales_by_type[i][start:end])
        print(robot_sales_by_type[i][start:end])


# ----------------------------------------------------
# 追加：年間 売上・支出・利益・累損 グラフ
# ----------------------------------------------------
# 累損（＝年間利益の累計）を計算
cumulative_loss = []
running = 0
for p in annual_profit:
    running += p
    cumulative_loss.append(running)

years_labels = [f"{y+1}年目" for y in range(years)]
months = list(range(1, MONTHS + 1))

# ----------------------------------------------------
# Plotly: 5段構成のサブプロット（収益部分は元コード準拠）
# ----------------------------------------------------
fig2_colors = ["#1F5DBA", "#F03531", "#7DBBFF", "#F5A3A3"]
fig_colors  = ["#1F5DBA", "#2E8B57", "#DAA520", "#ff9da7"]

with tab_graphs:

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=years_labels, y=annual_total, name="総売上"))
    fig2.add_trace(go.Bar(x=years_labels, y=annual_expense, name="総支出"))
    fig2.add_trace(go.Bar(x=years_labels, y=annual_profit, name="年間利益"))
    fig2.add_trace(go.Scatter(x=years_labels, y=cumulative_loss, name="累損（累計利益）", mode="lines+markers"))

    fig2.update_layout(
        title="売上・支出・利益・累損",
        barmode="group",
        colorway=fig2_colors
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[
            [{"secondary_y": False}],
            [{"secondary_y": False}],
        ],
        vertical_spacing=0.2,
        subplot_titles=[
            "総売上・販売手数料・アプリ収入",
            "販売台数"
        ]
    )


    # ④ 年間売上（総・手数料・アプリ）
    fig.add_trace(go.Bar(x=years_labels, y=annual_total, name="総売上"), row=1, col=1)
    fig.add_trace(go.Bar(x=years_labels, y=annual_commission, name="販売手数料収入"), row=1, col=1)
    fig.add_trace(go.Bar(x=years_labels, y=annual_app, name="アプリ収入"), row=1, col=1)

    # ⑤ 年間ロボット販売台数
    # 種類別 年間販売台数の棒グラフ
    for i in range(num_robot_types):
        fig.add_trace(
            go.Bar(
                x=years_labels,
                y=annual_robot_sales_by_type[i],
                name=f"{robot_names[i]}"
            ),
            row=2,
            col=1
        )

    fig.update_layout(
        height=600,
        barmode="group",
        title="売上げ・販売台数",
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
        colorway=fig_colors
    )

    st.plotly_chart(fig, use_container_width=True)


    fig = make_subplots(
        rows=3,
        cols=1,
        specs=[
            [{"secondary_y": False}],
            [{"secondary_y": True}],
            [{"secondary_y": True}],
        ],
        vertical_spacing=0.06,
        subplot_titles=[
            "販売会社数・イベント数",
            "新規ユーザー数（左軸）",
            "有料会員数（左軸）・アプリ収入（右軸）",
        ]
    )

    # ①
    fig.add_trace(go.Bar(x=months, y=contract_companies, name="販売会社数"), row=1, col=1)
    fig.add_trace(go.Bar(x=months, y=events_per_month, name="イベント数"), row=1, col=1)

    # ②
    fig.add_trace(go.Bar(x=months, y=new_users, name="新規ユーザー数", opacity=0.5),
                  row=2, col=1, secondary_y=False)

    # ③
    fig.add_trace(go.Bar(x=months, y=paying_users, name="有料会員数", opacity=0.5),
                  row=3, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=months, y=app_revenue, name="アプリ収入", mode="lines"),
                  row=3, col=1, secondary_y=True)


    fig.update_layout(
        height=1500,
        barmode="group",
        title="収益計算（ロボット販売 × アプリ課金）",
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
    )

    st.plotly_chart(fig, use_container_width=True)


    # 支出項目別 月次推移グラフ
    st.subheader("支出項目別 月次推移")

    # アプリ開発 月次推移グラフ
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(x=months, y=cost_app_android_initial, name="アプリ開発費（Android初期）"))
    fig3.add_trace(go.Bar(x=months, y=cost_app_ios_initial, name="アプリ開発費（iPhone初期）"))
    fig3.add_trace(go.Bar(x=months, y=cost_app_android_bugfix, name="アプリ不具合修正費（Android）"))
    fig3.add_trace(go.Bar(x=months, y=cost_app_ios_bugfix, name="アプリ不具合修正費（iPhone）"))

    fig3.update_layout(
        title="アプリ開発 月次推移",
        xaxis_title="月",
        yaxis_title="金額（円）",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=700,
    )

    st.plotly_chart(fig3, use_container_width=True)

    # クラウド費用 月次推移グラフ
    fig4 = go.Figure()

    fig4.add_trace(go.Bar(x=months, y=cost_cloud_initial_arr, name="クラウド初期構築費"))
    fig4.add_trace(go.Bar(x=months, y=cost_cloud_aws, name="AWS費用（有料会員数連動）"))
    fig4.add_trace(go.Bar(x=months, y=cost_cloud_bugfix_arr, name="クラウド不具合修正費", ))
    fig4.add_trace(go.Bar(x=months, y=cost_cloud_scale, name="クラウド増強費用", ))

    fig4.update_layout(
        title="クラウド費用 月次推移（全費目）",
        xaxis_title="月",
        yaxis_title="金額（円）",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=700,
    )

    st.plotly_chart(fig4, use_container_width=True)

    # その他 月次推移グラフ
    fig5 = go.Figure()

    fig5.add_trace(go.Bar(x=months, y=cost_shop_acquisition, name="販売店向けロボット・ツール費", ))
    fig5.add_trace(go.Bar(x=months, y=cost_customer_support, name="カスタマーサポート費", ))
    fig5.add_trace(go.Bar(x=months, y=cost_potstill_salary, name="事業体人件費", ))

    fig5.update_layout(
        title="その他 月次推移（全費目）",
        xaxis_title="月",
        yaxis_title="金額（円）",
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=700,
    )

    st.plotly_chart(fig5, use_container_width=True)





# ----------------------------------------------------
# サマリー
# ----------------------------------------------------
with (((((((tab_summary))))))):
    st.header("サマリー")

    st.write(f"📅 シミュレーション期間：**{years}年（{MONTHS}ヶ月）**")
    st.write(f"👥 最終月の有料会員数：**{paying_users[-1]:,.0f}人**")
    st.write(f"🏢 最終月の販売会社数：**{contract_companies[-1]:,.0f}社**")

    st.markdown("---")

    st.write(f"🤖 {years}年間のロボット販売台数：**{sum(new_users):,.0f}台**")
    st.write(f"💰 {years}年間の総売上：**{sum(total_revenue):,.0f}円**")
    st.write(f"💸 {years}年間の総支出：**{sum(total_expense):,.0f}円**")
    st.write(f"📈 {years}年間の累計利益：**{sum(profit):,.0f}円**")

    st.markdown("---")
    st.caption(f"{years}年間の売上内訳")

    st.write(f"💸 総アプリ課金：**{sum(app_revenue):,.0f}円**")
    st.write(f"💸 総販売手数料：**{sum(commission_revenue):,.0f}円**")

    st.markdown("---")
    st.caption(f"{years}年間の支出内訳")

    total_apl_expense = sum(cost_app_ios_initial) + sum(cost_app_android_initial) + sum(cost_app_ios_bugfix) + sum(cost_app_android_bugfix)
    st.write(f"💸 総アプリ開発費：**{total_apl_expense:,.0f}円**")

    total_cld_expense = sum(cost_cloud_initial_arr) + sum(cost_cloud_aws) + sum(cost_cloud_bugfix_arr) + sum(cost_cloud_scale)
    st.write(f"💸 総クラウド開発費：**{total_cld_expense:,.0f}円**")

    total_psl_expense = sum(potstill_fte) + sum(cost_potstill_salary)
    st.write(f"💸 総事業体人件費：**{total_psl_expense:,.0f}円**")

    st.write(f"💸 総販売ツール費：**{sum(cost_shop_acquisition):,.0f}円**")
    st.write(f"💸 総カスタマーサポート費：**{sum(cost_customer_support):,.0f}円**")



