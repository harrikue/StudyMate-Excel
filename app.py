import streamlit as st
import pandas as pd
from pathlib import Path
import re
from decimal import Decimal, InvalidOperation


def normalise_text(answer):
    """Standardise text without changing its meaning."""
    if answer is None:
        return ""

    answer = str(answer).strip().lower()

    # Replace multiple spaces, tabs and line breaks with one space.
    answer = re.sub(r"\s+", " ", answer)

    # Remove unnecessary punctuation around the answer.
    answer = answer.strip(" .,!?:;")

    # Ignore an introductory article for simple answers.
    answer = re.sub(r"^(a|an|the)\s+", "", answer)

    return answer


def convert_to_number(answer):
    """Convert a learner's numeric response into a Decimal."""
    if answer is None:
        return None

    value = str(answer).strip()

    if not value:
        return None

    # Allow common currency symbols and thousands separators.
    value = value.replace(",", "")
    value = re.sub(r"[£$€]", "", value)
    value = value.strip()

    try:
        number = Decimal(value)

        # Reject invalid values such as NaN and infinity.
        if not number.is_finite():
            return None

        return number

    except InvalidOperation:
        return None


def validate_answer(
    user_answer,
    correct_answer,
    answer_type="text",
    accepted_answers=None,
    tolerance=Decimal("0.01")
):
    """
    Validate text or numerical answers.

    Returns:
        (True, feedback) when the answer is correct.
        (False, feedback) when the answer is incorrect or missing.
    """

    # Check for a missing answer.
    if user_answer is None or str(user_answer).strip() == "":
        return False, "Please enter an answer before checking your work."

    # Numerical answer validation.
    if answer_type == "number":
        submitted_number = convert_to_number(user_answer)
        expected_number = convert_to_number(correct_answer)

        if expected_number is None:
            return False, "The expected answer could not be validated."

        if submitted_number is None:
            return False, (
                "Please enter a valid number. "
                "Check that your answer contains only numeric values."
            )

        if abs(submitted_number - expected_number) <= tolerance:
            return True, (
                "Well done! Your numerical answer is correct."
            )

        return False, (
            "Not quite. Check your calculation and try again. "
            "You can use a hint if you need help."
        )

    # Text answer validation.
    if answer_type == "text":
        submitted_text = normalise_text(user_answer)
        expected_text = normalise_text(correct_answer)

        # Include the main answer and any explicitly approved alternatives.
        possible_answers = [correct_answer]

        if accepted_answers:
            possible_answers.extend(accepted_answers)

        normalised_answers = {
            normalise_text(answer)
            for answer in possible_answers
            if answer is not None
        }

        if submitted_text in normalised_answers:
            return True, (
                "Well done! Your answer is correct."
            )

        return False, (
            "Not quite. Review the lesson and think about the "
            "Excel concept being described. Try again or request a hint."
        )

    return False, "This exercise has an unsupported answer type."
else:
            st.session_state.attempts[k]=st.session_state.attempts.get(k,0)+1
            if answers_match(ans, x[4]):
                st.success("Correct! Well done. "+x[7])
                st.session_state.completed=sorted(set(st.session_state.completed+[k]))
            else:
                st.warning("Not quite. Your answer doesn't match the expected answer yet. "+x[5]+" Review the worked example and try again.")
    if st.button("Read the lesson again",key=f"review_{k}"):
        open_lesson(m,l)

def project():
    st.title("Practical project: Analyse shop sales")
    st.write("Imagine you're helping a small shop understand its sales.")
    try: df=pd.read_excel(DATA)
    except Exception as e:
        st.error(f"Could not open the sample dataset: {e}"); return
    st.subheader("Sample dataset")
    st.caption("Each row represents one sale. Column letters and row numbers follow the layout used in Excel.")
    # Keep the original dataset unchanged for calculations. Format only the
    # display copy so Excel dates remain real date values and can still sort.
    excel_view = df.copy()
    excel_view["Date"] = pd.to_datetime(excel_view["Date"], errors="coerce")
    excel_view.columns = [
        f"{excel_column_name(i)} · {column}"
        for i, column in enumerate(excel_view.columns, start=1)
    ]
    excel_view.index = pd.RangeIndex(
        start=2, stop=len(excel_view) + 2, name="Row"
    )

    # Compact widths reduce unnecessary horizontal scrolling. The dataframe
    # keeps its own horizontal scroll on narrow screens rather than shrinking
    # text until it becomes unreadable.
    dataset_columns = {
        "A · Date": st.column_config.DateColumn(
            "A · Date", format="DD MMM YYYY", width="small"
        ),
        "B · Product": st.column_config.TextColumn(
            "B · Product", width="medium"
        ),
        "C · Category": st.column_config.TextColumn(
            "C · Category", width="small"
        ),
        "D · Region": st.column_config.TextColumn(
            "D · Region", width="small"
        ),
        "E · Salesperson": st.column_config.TextColumn(
            "E · Salesperson", width="medium"
        ),
        "F · Units Sold": st.column_config.NumberColumn(
            "F · Units Sold", format="%d", width="small"
        ),
        "G · Unit Price": st.column_config.NumberColumn(
            "G · Unit Price", format="£%.2f", width="small"
        ),
        "H · Revenue": st.column_config.NumberColumn(
            "H · Revenue", format="£%.2f", width="medium"
        ),
    }
    st.dataframe(
        excel_view,
        column_config=dataset_columns,
        use_container_width=True,
        height=min(620, 35 * (len(excel_view) + 1)),
    )
    st.caption(
        "On smaller screens, scroll horizontally within the table to view "
        "all columns. The worksheet data and Excel row references are unchanged."
    )
    st.download_button("Download sales dataset",DATA.read_bytes(),"StudyMate_sales_dataset.xlsx")
    st.subheader("Explore the results")
    a,b,c=st.columns(3)
    a.metric("Total revenue",f"£{df.Revenue.sum():,.2f}")
    b.metric("Average sale",f"£{df.Revenue.mean():,.2f}")
    region=st.selectbox("Choose a region",sorted(df.Region.unique()))
    regional=df[df.Region==region]
    c.metric(f"{region} revenue",f"£{regional.Revenue.sum():,.2f}")
    st.write(f"There are **{len(regional)}** transactions from {region}.")
    st.subheader("Project tasks")
    st.markdown('1. Calculate total revenue with `SUM`.\\n2. Find average revenue with `AVERAGE`.\\n3. Count regional transactions with `COUNTIF`.\\n4. Calculate regional revenue with `SUMIF`.')
    st.info('Try these formulas in Excel: `=SUM(H2:H27)`, `=AVERAGE(H2:H27)`, `=COUNTIF(D2:D27,"Scotland")`, `=SUMIF(D2:D27,"Scotland",H2:H27)`. Adjust ranges if needed.')
    reflection=st.text_area("What did you learn about the shop's sales?")
    if st.button("Save project reflection"):
        if reflection.strip(): st.session_state.project_reflection=reflection.strip(); st.success("Reflection saved for this session.")
        else: st.warning("Write a short reflection first.")

def progress():
    st.title("My Progress"); items=lessons(); done=len(st.session_state.completed)
    st.metric("Lessons completed",f"{done} of {len(items)}"); st.progress(done/len(items))
    for m,mod in enumerate(MODULES):
        n=sum(key(m,l) in st.session_state.completed for l in range(len(mod[2])))
        st.write(f"**{mod[0]}**: {n}/{len(mod[2])} lessons completed")
    st.write(f"Practice attempts this session: {sum(st.session_state.attempts.values())}")
    if st.button("Reset my progress"):
        st.session_state.completed=[]; st.session_state.attempts={}; st.session_state.hints={}
        st.success("Session progress reset.")

def main():
    init(); sidebar()
    page=st.session_state.page
    {"Home":home,"Learn":learn,"Lesson":lesson,"Practice":practice,"Sales Project":project,"My Progress":progress}.get(page,home)()

if __name__=="__main__": main()
