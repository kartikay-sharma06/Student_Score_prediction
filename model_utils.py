import os
import pickle
import numpy as np

DEFAULT_COLUMNS = [
    'Gender',
    'AttendanceRate',
    'StudyHoursPerWeek',
    'PreviousGrade',
    'ExtracurricularActivities',
    'ParentalSupport'
]

SCALER_MEAN = np.array([0.57142857, 85.57142857, 18.28571429, 78.42857143, 1.42857143, 1.28571429])
SCALER_STD = np.array([0.49487166, 8.15662996, 7.38172039, 10.79493456, 1.17803018, 0.88063057])
MODEL_INTERCEPT = 80.71428571428572
MODEL_COEF = np.array([-0.00782199672, 0.928257150, -0.894518277, 11.5115635, -0.224682257, -0.820313409])

class StudentScorePredictor:
    def __init__(self, model_path='LR_Student.pkl', scaler_path='scaler.pkl', columns_path='columns.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.columns_path = columns_path
        self.sklearn_available = False
        self.model = None
        self.scaler = None
        self.columns = DEFAULT_COLUMNS
        self._load_models()

    def _load_models(self):
        try:
            import joblib
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.sklearn_available = True
        except Exception:
            self.sklearn_available = False

        if os.path.exists(self.columns_path):
            try:
                with open(self.columns_path, 'rb') as f:
                    self.columns = pickle.load(f)
            except Exception:
                self.columns = DEFAULT_COLUMNS

    def encode_inputs(self, gender_str, attendance, study_hours, prev_grade, extra_activities, parental_str):
        gender_code = 1 if str(gender_str).strip().lower() == 'male' else 0
        parental_lower = str(parental_str).strip().lower()
        if parental_lower == 'high':
            parental_code = 2
        elif parental_lower == 'medium':
            parental_code = 1
        else:
            parental_code = 0

        attendance = float(attendance)
        study_hours = float(study_hours)
        prev_grade = float(prev_grade)
        extra_activities = float(extra_activities)

        features = np.array([
            gender_code,
            attendance,
            study_hours,
            prev_grade,
            extra_activities,
            parental_code
        ], dtype=float)

        return features

    def predict(self, gender, attendance, study_hours, prev_grade, extra_activities, parental_support):
        features = self.encode_inputs(gender, attendance, study_hours, prev_grade, extra_activities, parental_support)

        if self.sklearn_available and self.model is not None and self.scaler is not None:
            try:
                scaled_x = self.scaler.transform([features])
                raw_pred = float(self.model.predict(scaled_x)[0])
            except Exception:
                scaled_x = (features - SCALER_MEAN) / SCALER_STD
                raw_pred = float(MODEL_INTERCEPT + np.dot(scaled_x, MODEL_COEF))
        else:
            scaled_x = (features - SCALER_MEAN) / SCALER_STD
            raw_pred = float(MODEL_INTERCEPT + np.dot(scaled_x, MODEL_COEF))

        final_score = max(0.0, min(100.0, round(raw_pred, 1)))

        if final_score >= 90:
            letter_grade = 'A+'
            status = 'Outstanding'
            status_color = 'success'
        elif final_score >= 80:
            letter_grade = 'A'
            status = 'Very Good'
            status_color = 'primary'
        elif final_score >= 70:
            letter_grade = 'B'
            status = 'Satisfactory'
            status_color = 'info'
        elif final_score >= 60:
            letter_grade = 'C'
            status = 'Needs Improvement'
            status_color = 'warning'
        else:
            letter_grade = 'D'
            status = 'Critical / Remedial Needed'
            status_color = 'danger'

        return {
            'predicted_score': final_score,
            'letter_grade': letter_grade,
            'status': status,
            'status_color': status_color,
            'features': features
        }

    def generate_reasons(self, student_name, student_class, gender, attendance, study_hours, prev_grade, extra_activities, parental_support, predicted_score):
        reasons = []
        recommendations = []

        attendance = float(attendance)
        study_hours = float(study_hours)
        prev_grade = float(prev_grade)
        extra_activities = int(float(extra_activities))
        parental_str = str(parental_support).capitalize()

        if prev_grade >= 85:
            reasons.append({
                'factor': 'Academic Foundation (Previous Grade)',
                'impact': 'Strong Positive Influence (+)',
                'icon': 'bi-award',
                'type': 'positive',
                'detail': f"{student_name}'s prior score of {prev_grade:.1f}% demonstrates a solid grasp of core fundamentals, acting as the strongest upward driver for the predicted final grade."
            })
        elif prev_grade >= 75:
            reasons.append({
                'factor': 'Academic Foundation (Previous Grade)',
                'impact': 'Moderate Positive Influence (+)',
                'icon': 'bi-journal-check',
                'type': 'positive',
                'detail': f"With a previous grade of {prev_grade:.1f}%, the student has a steady base, positioning them well to maintain or enhance their performance."
            })
        else:
            reasons.append({
                'factor': 'Academic Foundation (Previous Grade)',
                'impact': 'Primary Growth Area (-)',
                'icon': 'bi-exclamation-triangle',
                'type': 'negative',
                'detail': f"A previous score of {prev_grade:.1f}% pulls down the baseline expectation, indicating that concept reinforcement is essential."
            })
            recommendations.append('Prioritize concept reviews and targeted practice tests on topics where previous exams lost marks.')

        if attendance >= 90:
            reasons.append({
                'factor': 'Class Attendance & Participation',
                'impact': 'Strong Consistency Boost (+)',
                'icon': 'bi-calendar-check',
                'type': 'positive',
                'detail': f"An attendance rate of {attendance:.1f}% ensures regular contact with lectures, active discussions, and immediate doubt clearance."
            })
        elif attendance >= 80:
            reasons.append({
                'factor': 'Class Attendance & Participation',
                'impact': 'Steady Presence (Neutral to Positive)',
                'icon': 'bi-calendar3',
                'type': 'neutral',
                'detail': f"Attendance is acceptable at {attendance:.1f}%, but aiming for 90%+ will help capture key revision topics before final exams."
            })
            recommendations.append(f"Try to maintain attendance above 90% in {student_class} to maximize classroom insights.")
        else:
            reasons.append({
                'factor': 'Class Attendance & Participation',
                'impact': 'Attendance Risk Factor (-)',
                'icon': 'bi-calendar-x',
                'type': 'negative',
                'detail': f"Attendance at {attendance:.1f}% is below optimal thresholds, risking knowledge gaps and missed syllabus coverage."
            })
            recommendations.append('Improve attendance consistency to avoid missing foundational classroom discussions.')

        if study_hours >= 20:
            reasons.append({
                'factor': 'Study Dedication',
                'impact': 'High Commitment (+)',
                'icon': 'bi-clock-history',
                'type': 'positive',
                'detail': f"Devoting {study_hours:.1f} hours/week outside class provides substantial time for revision, problem-solving, and mock tests."
            })
        elif study_hours >= 14:
            reasons.append({
                'factor': 'Study Dedication',
                'impact': 'Balanced Study Routine',
                'icon': 'bi-clock',
                'type': 'neutral',
                'detail': f"A moderate study schedule of {study_hours:.1f} hours/week provides steady coverage, though increasing focused self-study during exam prep can unlock higher tiers."
            })
        else:
            reasons.append({
                'factor': 'Study Dedication',
                'impact': 'Low Time Allocation (-)',
                'icon': 'bi-hourglass-bottom',
                'type': 'negative',
                'detail': f"At {study_hours:.1f} hours per week, independent study time is limited, making it harder to thoroughly master complex subjects."
            })
            recommendations.append('Establish a structured daily study plan aiming for at least 15 to 20 hours per week.')

        if parental_str == 'High':
            reasons.append({
                'factor': 'Home Support & Mentorship',
                'impact': 'High Encouragement Environment (+)',
                'icon': 'bi-people',
                'type': 'positive',
                'detail': 'Active parental involvement and guidance foster accountability, emotional support, and a distraction-free learning environment.'
            })
        elif parental_str == 'Medium':
            reasons.append({
                'factor': 'Home Support & Mentorship',
                'impact': 'Stable Support System',
                'icon': 'bi-person-check',
                'type': 'neutral',
                'detail': 'Moderate parental support maintains healthy independence while offering timely check-ins.'
            })
        else:
            reasons.append({
                'factor': 'Home Support & Mentorship',
                'impact': 'Self-Reliance Needed',
                'icon': 'bi-person',
                'type': 'neutral',
                'detail': 'With low parental support, proactive mentorship from teachers, study groups, and school counselors is beneficial.'
            })
            recommendations.append('Engage with peer study groups or teacher office hours for extra feedback and mentorship.')

        if 1 <= extra_activities <= 2:
            reasons.append({
                'factor': 'Co-Curricular Engagement',
                'impact': 'Healthy Balance (+)',
                'icon': 'bi-trophy',
                'type': 'positive',
                'detail': f"Participation in {extra_activities} activity/activities offers healthy mental relief and time management skills without encroaching on academics."
            })
        elif extra_activities >= 3:
            reasons.append({
                'factor': 'Co-Curricular Engagement',
                'impact': 'Heavy Schedule Commitment',
                'icon': 'bi-activity',
                'type': 'neutral',
                'detail': f"Participating in {extra_activities} activities demonstrates broad talent, but time allocation should be guarded during exam periods."
            })
            recommendations.append('Maintain time management discipline so intensive extracurricular schedules do not compress exam revision windows.')
        else:
            reasons.append({
                'factor': 'Co-Curricular Engagement',
                'impact': 'Focused Solely on Academics',
                'icon': 'bi-book',
                'type': 'neutral',
                'detail': 'While zero extracurriculars leaves maximum time for studies, adding light recreational activities can enhance focus and prevent burnout.'
            })

        if not recommendations:
            recommendations.append('Maintain current study routines and consistent attendance to secure top-tier results in final examinations.')

        return {
            'reasons': reasons,
            'recommendations': recommendations
        }
