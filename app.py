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

    st.title("Your learning pathway")
    st.write("Work through the modules in order. You can revisit any lesson.")
    for m,mod in enumerate(MODULES):
        count=sum(key(m,l) in st.session_state.completed for l in range(len(mod[2])))
        with st.expander(f"Module {m+1}: {mod[0]} · {count}/{len(mod[2])} completed",expanded=(m==0)):
            st.write(mod[1])
            for l,x in enumerate(mod[2]):
                c1,c2=st.columns([4,1])
                with c1: st.write(("✓ " if key(m,l) in st.session_state.completed else "")+x[0])
                with c2:
                    if st.button("Open",key=f"open_{m}_{l}"): open_lesson(m,l)

def lesson():
    m,l=st.session_state.module,st.session_state.lesson; mod=MODULES[m]; x=mod[2][l]
    st.caption(f"Module {m+1}: {mod[0]} / Lesson {l+1}")
    st.title(x[0]); st.subheader("What you'll learn"); st.write(x[1])
    st.subheader("Worked example"); st.info(x[2])
    st.subheader("Try it yourself")
    st.write(x[3])
    st.caption("This question checks the idea you have just learned. Use the worked example as a guide, then try it without looking at the answer.")
    if st.button("Practise this lesson",type="primary"):
        go("Practice")
    if st.button("Back to Learning Path"): go("Learn")

def practice():
    st.title("Practice")
    st.write("Use what you have just learned. Choose guided support, hints or an independent attempt.")
    items=lessons()
    labels=[f"{MODULES[m][0]} · {x[0]}" for m,l,x in items]
    default_idx=min(st.session_state.get("practice_lesson_index", 0), len(items)-1)
    idx=st.selectbox(
        "Lesson to practise", range(len(items)), index=default_idx,
        format_func=lambda i: labels[i], key="practice_lesson_selector"
    )
    st.session_state.practice_lesson_index=idx
    m,l,x=items[idx]; k=key(m,l)

    st.caption(f"Module {m+1}: {MODULES[m][0]} / Lesson {l+1}")
    st.subheader("Remember the lesson")
    with st.expander("Review the explanation and worked example", expanded=True):
        st.markdown(f"**Key idea**  \n{x[1]}")
        st.info(x[2])
    st.subheader("Your exercise")
    st.write(x[3])

    level=st.radio("Choose your support level",["Guided","With hints","Independent"],horizontal=True,key=f"level_{k}")
    if level=="Guided":
        st.info("Start by applying the key idea above to this question.")
        st.markdown(f"**Step 1:** {x[5]}")
        st.caption("Use the worked example to help you decide what to do next. Enter your own answer below.")
    elif level=="With hints":
        if st.button("Show next hint",key=f"hintbtn_{k}"):
            st.session_state.hints[k]=min(st.session_state.hints.get(k,0)+1,2)
        n=st.session_state.hints.get(k,0)
        if n>=1: st.info("Hint 1: "+x[5])
        if n>=2: st.info("Hint 2: "+x[6])
        if n==0: st.caption("Hints are revealed one at a time so you can still work out the answer yourself.")
    else:
        st.caption("No hints are shown. Try to answer using what you remember from the lesson.")

    ans=st.text_input("Your answer",key=f"answer_{k}",placeholder="Type your answer")
    if st.button("Check My Answer",type="primary",key=f"check_{k}"):
        if not ans.strip():
            st.warning("Enter an answer first.")
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
    excel_view=df.copy()
    excel_view.columns=[f"{excel_column_name(i)} · {column}" for i,column in enumerate(df.columns, start=1)]
    excel_view.index=pd.RangeIndex(start=2, stop=len(excel_view)+2, name="Row")
    st.dataframe(excel_view,use_container_width=True)
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

