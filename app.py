from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys




app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

CURRENT_SURVEY_KEY = "current_survey"
RESPONSES_KEY = "responses"


@app.route('/')
def show_survey_intro():
    """show survery start button"""
    return render_template('survey.html', surveys=surveys)


@app.route('/', methods=["POST"])
def pick_survey():
    """initialize survey session"""
    survey_name = request.form['survey']

    survey = surveys[survey_name]
    session[CURRENT_SURVEY_KEY] = survey_name
    session[RESPONSES_KEY] = []

    return render_template("start_survey.html", survey=survey)
  

@app.route('/start', methods=["POST"])
def start_survey():
    """initialize survey session"""
    session[RESPONSES_KEY] = []
    return redirect("/question/0")


@app.route('/answer', methods=["POST"])
def answer():
    """handle the answer"""
    #collect the answer from the post
    answer = request.form['answer']
    text = request.form.get('text', "")
    #set responses from session[RESPONSES_KEY]
    responses = session[RESPONSES_KEY]
    survey_name = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_name]

    #Validate an answer was given
    if(answer is ""):
        flash("We need an answer!!", "error")
        return redirect(f"/question/{len(responses)}")

    #Add answer to responses
    responses.append({ "answer": answer, "text": text })
    session[RESPONSES_KEY] = responses

    #If we've reached the length of survey.questions redirect to "completed"
    if(len(responses) == len(survey.questions)):
        return redirect("/completed")
    #Else next question
    else:
        return redirect(f"/question/{len(responses)}")



@app.route('/question/<int:qid>')
def show_question(qid):
    #Set responses from session
    responses = session.get(RESPONSES_KEY)

    survey_name = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_name]
    #If there are no response start at the begining
    if(responses is None):
        return redirect("/")
    #If we reach survey.questions length redirect to "completed"
    if(len(responses) == len(survey.questions)):
        return redirect("/completed")

    #If the url number is invalid, stay on current question and flash error msg
    if(len(responses) != qid):
        flash(f"Invalid question id: {qid}", "error")
        return redirect(f"/question/{len(responses)}")
    
    #If we pass all previous cases return questions template with the right question
    question = survey.questions[qid]
    return render_template("question.html", question_num=qid, question=question)


@app.route("/completed")
def complete():
    #Render completed form success message
    responses = session.get(RESPONSES_KEY)
    survey_name = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_name]


    return render_template("survey_completed.html", survey=survey, responses=responses)
    