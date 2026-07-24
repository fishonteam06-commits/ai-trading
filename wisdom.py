"""
wisdom.py
----------
PROVEN principles from famous traders and trading books — in plain English.
These are the actual principles drawn from research (no copyrighted text,
only the principles + attribution). Shown in a Streamlit tab via render().
"""

import streamlit as st


# (Principle, detail, source) — money management
MONEY_RULES = [
    ("1% / 2% Risk Rule",
     "Risk only 1-2% of your total capital on any single trade. That way, even if "
     "you lose 10 trades in a row, your account survives.",
     "Turtle Traders / Van Tharp"),
    ("Cut losses, let winners run",
     "Exit losing trades QUICKLY (stop-loss), and let winning trades run. "
     "This one phrase is the secret behind most successful traders.",
     "Richard Dennis (Turtles)"),
    ("Risk-Reward of at least 1:2",
     "Set your target at least DOUBLE the risk you're taking (down to your stop). "
     "That way you stay profitable even if half your trades go wrong.",
     "Classic money management"),
    ("Pyramiding (thoughtfully)",
     "Add to a position only when the trade moves in your favour — don't pour more "
     "money into a losing trade by 'averaging down'.",
     "Turtle Traders"),
    ("Never put all your capital in one place",
     "Diversify — don't bet everything on a single coin/stock. If one sinks, not all of it sinks.",
     "Common wisdom"),
]

# Trading psychology — the core ideas from Mark Douglas (Trading in the Zone)
PSYCH_RULES = [
    ("Think in probabilities, not certainties",
     "Any single trade can win or lose — that's normal. Your job is simply to repeat "
     "your 'edge' again and again; profit is built over a set of 100 trades, not one.",
     "Mark Douglas"),
    ("Process > Outcome",
     "Don't judge a trade by its result — judge it by how well you followed your plan. "
     "A good trade is one taken according to plan, even if it lost.",
     "Mark Douglas"),
    ("Fear and Greed are the biggest enemies",
     "Fear makes you miss good trades; greed makes you take bad ones. "
     "Write your rules in advance and stick to them — don't decide on emotion.",
     "Mark Douglas"),
    ("Discipline = Consistency",
     "Even a brilliant strategy loses without discipline. The same rules, the same "
     "risk, the same patience every day — it feels boring, but that's what wins.",
     "Trading in the Zone"),
    ("Avoid revenge trading",
     "Don't rush into a trade to 'win it back' right after a loss — "
     "that usually leads to an even bigger loss. Take a break, then think.",
     "Pro traders"),
]

# Pre-trade checklist (before every trade)
CHECKLIST = [
    "Is the trend in my direction? (Did I check the Multi-Timeframe tab?)",
    "Is my reason for entry clear? (Do at least 2-3 signals agree?)",
    "Where will my stop-loss go — decided in advance?",
    "Where is my target — is the Risk:Reward 1:2 or better?",
    "Am I risking only 1-2% on this trade? (Did I use the Risk Calculator?)",
    "Am I free of emotion (fear/greed/revenge)? Is my head clear?",
]


def render() -> None:
    st.subheader("🎓 Proven Principles from Pro Traders")
    st.caption("These are the actual principles from the world's famous traders and "
               "trading books — learn them and apply them. More than any strategy, "
               "these principles protect your money.")

    st.markdown("### 💰 Money Management (the rules that protect your capital)")
    for title, detail, src in MONEY_RULES:
        with st.container(border=True):
            st.markdown(f"**{title}**  \n{detail}")
            st.caption(f"— {src}")

    st.markdown("### 🧠 Trading Psychology (mastering your mind)")
    st.caption("Core ideas from the famous book *'Trading in the Zone'* (Mark Douglas):")
    for title, detail, src in PSYCH_RULES:
        with st.container(border=True):
            st.markdown(f"**{title}**  \n{detail}")
            st.caption(f"— {src}")

    st.markdown("### ✅ Before Every Trade — Checklist")
    st.write("Ask yourself these 6 questions BEFORE every trade. If even one answer is 'no', don't take the trade:")
    for i, item in enumerate(CHECKLIST, 1):
        st.checkbox(f"{i}. {item}", key=f"chk_{i}")

    st.info("💡 **The biggest lesson:** A successful trader isn't the one who's always "
            "right — it's the one who keeps losses small and follows their rules with discipline.")

    st.caption("Sources: Turtle Traders (Richard Dennis), 'Trading in the Zone' (Mark Douglas), "
               "classic money-management principles. For educational purposes only.")
