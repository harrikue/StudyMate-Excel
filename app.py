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

st.set_page_config(page_title="StudyMate Excel", page_icon="📘", layout="wide")
DATA = Path(__file__).parent / "data" / "sales_dataset.xlsx"

MODULES = [
("Excel Basics", "Understand workbooks, worksheets, rows, columns and cells.", [
("Meet the spreadsheet", "A workbook is an Excel file. It contains worksheets. A worksheet has rows and columns. A cell is one box where a row and column meet.", "Cell B3 is in column B and row 3.", "What is the name of one box where a row and column meet?", "cell", "It is where a row and column meet.", "The answer starts with C.", "How would you explain the difference between a row and a column?"),
("Enter and organise data", "Click a cell and type. You can enter text, numbers and dates. Numbers can be used in calculations.", "A shop might enter Apples in A2 and 12 in B2.", "What type of data is 25 when entered as a number?", "number", "It can be used in a calculation.", "It is not text or a date.", "What information might a shop record?")
]),
("Formulas and Calculations", "Use formulas to make Excel calculate for you.", [
("Create your first formula", "A formula tells Excel to calculate something. Every formula starts with an equals sign. Cell references let Excel use values stored in cells.", "If A1 contains 5 and A2 contains 3, =A1+A2 returns 8.", "What symbol must appear first in an Excel formula?", "=", "It is the symbol used to show equality.", "It looks like two short horizontal lines.", "Why are cell references useful when values change?")
]),
("Essential Excel Functions", "Learn SUM, AVERAGE, COUNTIF and SUMIF.", [
("Add values with SUM", "SUM adds numbers in a range. It is useful for totals such as daily sales.", "If sales are in B2:B4, =SUM(B2:B4) adds them.", "Sales are £12, £18 and £10. What is the total?", "40", "Add the three sales values.", "12 + 18 + 10 = ?", "When might a shop use SUM?"),
("Find the mean with AVERAGE", "AVERAGE adds values and divides by how many values there are. It helps describe a typical transaction.", "For 10, 20 and 30, =AVERAGE(A1:A3) returns 20.", "Find the average of 10, 20 and 30.", "20", "Add the values, then divide by how many there are.", "The total is 60. Divide by 3.", "How could average sales help a shop owner?"),
("Count matching values with COUNTIF", "COUNTIF counts how many cells meet one condition, such as how many sales came from Scotland.", '=COUNTIF(D2:D27,"Scotland") counts Scotland entries.', "A list contains Scotland, Wales, Scotland. How many entries are Scotland?", "2", "Count only the entries that say Scotland.", "Scotland appears twice.", "What other category could you count?"),
("Add matching values with SUMIF", "SUMIF checks one range for a condition and adds matching values from another range.", '=SUMIF(D2:D27,"Scotland",H2:H27) adds revenue for Scotland.', "Scotland sales are 12 and 8. Wales sales are 5. What is the Scotland total?", "20", "Ignore the Wales value.", "Add 12 and 8.", "How is SUMIF different from COUNTIF?")
]),
("Sorting and Filtering Data", "Find information quickly in a list of records.", [
("Sort and filter a list", "Sorting changes the order of records. Filtering temporarily shows only records that match a condition.", "Sort revenue largest to smallest to find top sales. Filter Region to show Scotland only.", "You want to see only sales from Scotland. Should you sort or filter?", "filter", "You want to hide other regions temporarily.", "Filtering displays only matching records.", "When would sorting be more useful?")
]),
("Practical Sales Analysis Project", "Apply your new skills to a small shop's sales.", [
("Explore the sales dataset", "A sales dataset stores one transaction per row. Use totals, averages and regional results to understand performance.", "Use SUM on Revenue for total revenue and AVERAGE for the average transaction.", "Which function adds revenue for Scotland only?", "sumif", "You need to add values that meet a condition.", "The function name combines SUM and IF.", "What business question could you answer?")
])
]

def key(m,l): return f"{m}-{l}"
def lessons(): return [(m,l,x) for m,mod in enumerate(MODULES) for l,x in enumerate(mod[2])]
def init():
    for k,v in {"page":"Home","module":0,"lesson":0,"completed":[],"attempts":{},"hints":{}}.items():
        if k not in st.session_state: st.session_state[k]=v
def go(page): st.session_state.page=page; st.rerun()
def open_lesson(m,l): st.session_state.module=m; st.session_state.lesson=l; go("Lesson")

def sidebar():
    st.sidebar.title("📘 StudyMate Excel")
    st.sidebar.caption("Your friendly guide to Excel")
    for p in ["Home","Learn","Practice","Sales Project","My Progress"]:
        if st.sidebar.button(p, use_container_width=True, type="primary" if st.session_state.page==p else "secondary"): go(p)
    st.sidebar.divider()
    st.sidebar.caption(f"Lessons completed: {len(st.session_state.completed)}/{len(lessons())}")
    st.sidebar.progress(len(st.session_state.completed)/len(lessons()))

def home():
    st.title("Welcome to StudyMate Excel! 👋")
    st.write("Learn Excel step by step, even if you've never used it before.")
    items=lessons(); done=len(st.session_state.completed)
    a,b=st.columns([2,1])
    nxt=next((x for x in items if key(x[0],x[1]) not in st.session_state.completed),None)
    with a:
        st.subheader("Continue learning")
        if nxt:
            m,l,x=nxt; st.info(f"**{x[0]}**  \n{MODULES[m][0]} · About 5 minutes")
            if st.button("Continue Learning",type="primary"): open_lesson(m,l)
        else:
            st.success("You've completed all lessons. Try the sales project.")
            if st.button("Open Sales Project",type="primary"): go("Sales Project")
    with b:
        st.subheader("Your progress"); st.metric("Lessons completed",f"{done}/{len(items)}"); st.progress(done/len(items))
    st.subheader("Your learning pathway")
    for i,mod in enumerate(MODULES):
        c1,c2=st.columns([4,1])
        with c1:
            st.markdown(f"**{i+1}. {mod[0]}**"); st.caption(mod[1])
        with c2:
            if st.button("Explore",key=f"home_{i}"): go("Learn")

def learn():
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
    st.subheader("Try it yourself"); st.write(x[3])
    if st.button("Go to Practice",type="primary"): go("Practice")
    if st.button("Back to Learning Path"): go("Learn")

def practice():
    st.title("Practice")
    st.write("Start with a little help, then try a question on your own.")
    items=lessons(); labels=[f"{MODULES[m][0]} · {x[0]}" for m,l,x in items]
    idx=st.selectbox("Choose a lesson",range(len(items)),format_func=lambda i:labels[i])
    m,l,x=items[idx]; k=key(m,l)
    st.subheader("Your task"); st.write(x[3])
    level=st.radio("Practice level",["Guided","With hints","Independent"],horizontal=True,key=f"level_{k}")
    if level=="Guided": st.info("1. Read the question.  2. Recall the lesson.  3. Enter your answer.")
    if level=="With hints":
        if st.button("Show next hint",key=f"hintbtn_{k}"):
            st.session_state.hints[k]=min(st.session_state.hints.get(k,0)+1,2); st.rerun()
        n=st.session_state.hints.get(k,0)
        if n>=1: st.info("Hint 1: "+x[5])
        if n>=2: st.info("Hint 2: "+x[6])
    ans=st.text_input("Your answer",key=f"answer_{k}",placeholder="Type your answer")
    if st.button("Check My Answer",type="primary",key=f"check_{k}"):
        if not ans.strip(): st.warning("Enter an answer first.")
        else:
            expected=x[4].strip().lower()
            submitted=ans.strip().lower().replace("£","").replace(",","")
            st.session_state.attempts[k]=st.session_state.attempts.get(k,0)+1
            if submitted==expected:
                st.success("Correct! Well done. "+x[7])
                st.session_state.completed=sorted(set(st.session_state.completed+[k]))
            else: st.warning("Not quite. That's okay. "+x[5]+" Try again or choose With hints for more support.")
    if st.button("Read the lesson again",key=f"review_{k}"): open_lesson(m,l)

def project():
    st.title("Practical project: Analyse shop sales")
    st.write("Imagine you're helping a small shop understand its sales.")
    try: df=pd.read_excel(DATA)
    except Exception as e:
        st.error(f"Could not open the sample dataset: {e}"); return
    st.subheader("Sample dataset"); st.caption("Each row represents one sale.")
    st.dataframe(df,use_container_width=True,hide_index=True)
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
