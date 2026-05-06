import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report, log_loss
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("final_training_data.csv")

features = [
    'Home_Team_Points', 'Away_Team_Points',
    'Home_Rank', 'Away_Rank',
    'Home_Form_5', 'Away_Form_5',
    'Attendance' 
]
target = 'Target'

test_size = 500 
train_df = df.iloc[:-test_size]
test_df = df.iloc[-test_size:]

X_train = train_df[features]
y_train = train_df[target]
X_test = test_df[features]
y_test = test_df[target]

print(f"Training on {len(X_train)} older matches.")
print(f"Testing on {len(X_test)} recent matches.")

print("\n--- 1. Baseline: Logistic Regression ---")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

log_reg = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
log_reg.fit(X_train_scaled, y_train)

y_pred_lr = log_reg.predict(X_test_scaled)
y_prob_lr = log_reg.predict_proba(X_test_scaled)

print(f"Accuracy: {accuracy_score(y_test, y_pred_lr):.4f}")
print(f"Log Loss: {log_loss(y_test, y_prob_lr):.4f}")
print(classification_report(y_test, y_pred_lr, target_names=['Home', 'Draw', 'Away'], zero_division=0))

print("\n--- 2. XGBoost Classifier ---")
xgb_clf = xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=3,
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    eval_metric='mlogloss'
)

xgb_clf.fit(X_train, y_train)

y_pred_xgb = xgb_clf.predict(X_test)
y_prob_xgb = xgb_clf.predict_proba(X_test)

print(f"Accuracy: {accuracy_score(y_test, y_pred_xgb):.4f}")
print(f"Log Loss: {log_loss(y_test, y_prob_xgb):.4f}")
print(classification_report(y_test, y_pred_xgb, target_names=['Home', 'Draw', 'Away'], zero_division=0))


# VISUALIZATIONS

def plot_cm(y_true, y_pred, title, filename):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Pred Home', 'Pred Draw', 'Pred Away'],
                yticklabels=['Actual Home', 'Actual Draw', 'Actual Away'])
    plt.title(title)
    plt.ylabel('True Outcome')
    plt.xlabel('Predicted Outcome')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

print("\nGenerating Confusion Matrices...")
plot_cm(y_test, y_pred_lr, 'Confusion Matrix: Logistic Regression', 'cm_logreg.png')
plot_cm(y_test, y_pred_xgb, 'Confusion Matrix: XGBoost', 'cm_xgb.png')

print("Generating Logistic Regression Plot...")
abs_coefs = np.mean(np.abs(log_reg.coef_), axis=0)
lr_importance = pd.DataFrame({
    'Feature': features,
    'Importance': abs_coefs
}).sort_values('Importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=lr_importance, palette='magma')
plt.title('Logistic Regression: Feature Importance (Mean Abs Coefficients)')
plt.tight_layout()
plt.savefig('feat_importance_logreg.png')
plt.close()

print("Generating XGBoost Plot...")
xgb_importance = pd.DataFrame({
    'Feature': features,
    'Importance': xgb_clf.feature_importances_
}).sort_values('Importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=xgb_importance, palette='viridis')
plt.title('XGBoost: Feature Importance (Gini/Gain)')
plt.tight_layout()
plt.savefig('feat_importance_xgb.png')
plt.close()

print("\nAll 4 plots saved")