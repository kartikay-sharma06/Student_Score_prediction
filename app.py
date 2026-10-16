from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import datetime
from model_utils import StudentScorePredictor

application = Flask(__name__)
app=application
app.secret_key = os.environ.get('SECRET_KEY', 'student-score-predictor-secret-key-2026')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'LR_Student.pkl')
scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
columns_path = os.path.join(BASE_DIR, 'columns.pkl')

predictor = StudentScorePredictor(
    model_path=model_path,
    scaler_path=scaler_path,
    columns_path=columns_path
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        student_name = request.form.get('student_name', '').strip()
        student_class = request.form.get('student_class', '').strip()

        if not student_name:
            flash("Please enter the student's name for reference.", 'warning')
            return redirect(url_for('index'))

        if not student_class:
            flash("Please enter the student's class or section for reference.", 'warning')
            return redirect(url_for('index'))

        gender = request.form.get('gender', 'Male').strip()
        attendance_rate = float(request.form.get('attendance_rate', 85))
        study_hours = float(request.form.get('study_hours', 15))
        previous_grade = float(request.form.get('previous_grade', 75))
        extracurricular = int(request.form.get('extracurricular', 1))
        parental_support = request.form.get('parental_support', 'Medium').strip()

        if not (0 <= attendance_rate <= 100):
            flash('Attendance Rate must be between 0% and 100%.', 'danger')
            return redirect(url_for('index'))

        if not (0 <= study_hours <= 168):
            flash('Study Hours per week must be between 0 and 168 hours.', 'danger')
            return redirect(url_for('index'))

        if not (0 <= previous_grade <= 100):
            flash('Previous Grade must be between 0 and 100.', 'danger')
            return redirect(url_for('index'))

        if extracurricular < 0:
            flash('Extracurricular activities count cannot be negative.', 'danger')
            return redirect(url_for('index'))

        prediction_result = predictor.predict(
            gender=gender,
            attendance=attendance_rate,
            study_hours=study_hours,
            prev_grade=previous_grade,
            extra_activities=extracurricular,
            parental_support=parental_support
        )

        analysis = predictor.generate_reasons(
            student_name=student_name,
            student_class=student_class,
            gender=gender,
            attendance=attendance_rate,
            study_hours=study_hours,
            prev_grade=previous_grade,
            extra_activities=extracurricular,
            parental_support=parental_support,
            predicted_score=prediction_result['predicted_score']
        )

        input_data = {
            'student_name': student_name,
            'student_class': student_class,
            'gender': gender,
            'attendance_rate': attendance_rate,
            'study_hours': study_hours,
            'previous_grade': previous_grade,
            'extracurricular': extracurricular,
            'parental_support': parental_support,
            'assessment_date': datetime.datetime.now().strftime('%B %d, %Y')
        }

        return render_template(
            'result.html',
            student=input_data,
            result=prediction_result,
            reasons=analysis['reasons'],
            recommendations=analysis['recommendations']
        )

    except ValueError as ve:
        flash(f'Invalid numeric input: {str(ve)}. Please check your entries.', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An unexpected error occurred during prediction: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json(force=True)
    try:
        student_name = data.get('student_name', 'Student')
        student_class = data.get('student_class', 'General')
        gender = data.get('gender', 'Male')
        attendance = float(data.get('attendance_rate', 85))
        study_hours = float(data.get('study_hours', 15))
        prev_grade = float(data.get('previous_grade', 75))
        extra = int(data.get('extracurricular', 1))
        parental = data.get('parental_support', 'Medium')

        pred_res = predictor.predict(gender, attendance, study_hours, prev_grade, extra, parental)
        analysis = predictor.generate_reasons(student_name, student_class, gender, attendance, study_hours, prev_grade, extra, parental, pred_res['predicted_score'])

        return jsonify({
            'status': 'success',
            'student_name': student_name,
            'student_class': student_class,
            'prediction': pred_res,
            'reasons': analysis['reasons'],
            'recommendations': analysis['recommendations']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Student Score Predictor Web App'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
