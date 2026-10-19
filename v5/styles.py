APP_STYLE = """
/* =========================================================
   COBOTICS DESIGN SYSTEM
   ========================================================= */

QMainWindow,
QWidget {
    background-color: #F8EFE5;
}

QLabel {
    color: #2F1E12;
    background: transparent;
}

/* =========================================================
   DEFAULT BUTTONS
   ========================================================= */
QPushButton,
QToolButton {
    background-color: #FFFDFC;
    color: #3A2616;
    border: 1px solid #D2BDA7;
    border-radius: 16px;
    padding: 10px 16px;
}

QPushButton:hover,
QToolButton:hover {
    background-color: #F1E3D4;
    border-color: #B89067;
}

QPushButton:pressed,
QToolButton:pressed {
    background-color: #DFC9B4;
}

/* =========================================================
   HOME PAGE
   ========================================================= */
QWidget#homePage {
    background-color: #F8EFE5;
}

QLabel#homeLogo {
    background: transparent;
}

QLabel#heroSubtitle {
    color: #7C6A5A;
}

QLabel#homeHint {
    color: #A38366;
}

QPushButton#startButton {
    background-color: #3A2616;
    color: #FFFDFC;
    border: 2px solid #3A2616;
    border-radius: 24px;
    padding: 12px 22px;
}

QPushButton#startButton:hover {
    background-color: #5A3B25;
    border-color: #5A3B25;
}

QPushButton#startButton:pressed {
    background-color: #2F1E12;
    border-color: #2F1E12;
}

QPushButton#secondaryActionButton {
    background-color: #FFFDFC;
    color: #3A2616;
    border: 1px solid #D2BDA7;
    border-radius: 19px;
    padding: 9px 14px;
}

QPushButton#secondaryActionButton:hover {
    background-color: #F0E2D4;
    border-color: #B89067;
}

QPushButton#secondaryActionButton:pressed {
    background-color: #DFC9B4;
}

/* =========================================================
   PERSISTENT SAFETY BAR
   ========================================================= */
QWidget#safetyBar {
    background-color: #F8EFE5;
    border: none;
    border-bottom: 1px solid #DDCDBD;
}

QWidget#statusCluster {
    background-color: #FCF7F1;
    border: 1px solid #E1D0BF;
    border-radius: 15px;
}

QFrame#statusSeparator {
    background-color: #DCC8B5;
    border: none;
    min-width: 1px;
    max-width: 1px;
    min-height: 18px;
    max-height: 18px;
}

QLabel#safetyReadyChip,
QLabel#safetyActiveChip,
QLabel#safetyNeutralChip,
QLabel#safetyDangerChip {
    background: transparent;
    border: none;
    padding-left: 8px;
    padding-right: 8px;
    font-weight: 700;
}

QLabel#safetyReadyChip {
    color: #4F6848;
}

QLabel#safetyActiveChip {
    color: #8A5D38;
}

QLabel#safetyNeutralChip {
    color: #876448;
}

QLabel#safetyDangerChip {
    color: #A32620;
}

QPushButton#estopButton {
    background-color: #B72A22;
    color: #FFFFFF;
    border: 2px solid #922019;
    border-radius: 15px;
    padding: 4px 14px;
    font-weight: 800;
}

QPushButton#estopButton:hover {
    background-color: #C73A31;
}

QPushButton#estopButton:pressed {
    background-color: #8F1D18;
}

QPushButton#estopButton[active="true"] {
    background-color: #8F1D18;
    border-color: #64130F;
}

/* =========================================================
   PAGE HEADERS / BACK BUTTON
   ========================================================= */
QLabel#pageTitle {
    color: #2F1E12;
}

QPushButton#pageBackButton {
    background-color: transparent;
    color: #3A2616;
    border: none;
    border-radius: 18px;
    padding: 0px;
}

QPushButton#pageBackButton:hover {
    background-color: #EADBCB;
}

QPushButton#pageBackButton:pressed {
    background-color: #DFC9B4;
}

/* =========================================================
   RUNNING PAGE
   ========================================================= */
QWidget#runningPage {
    background-color: #F8EFE5;
}

QLabel#runningEyebrow {
    color: #A17D5D;
    font-weight: 800;
    letter-spacing: 2px;
}

QLabel#runningArtIcon {
    background-color: #FFFDFC;
    border: 1px solid #E1D0BF;
    border-radius: 28px;
    padding: 8px;
}

QLabel#runningTitle {
    color: #2F1E12;
}

QLabel#runningStage {
    color: #7A5538;
    font-weight: 700;
}

QLabel#runningInfo {
    color: #7C6A5A;
}

QLabel#progressText {
    color: #7A5538;
    font-weight: 800;
}

QProgressBar#pourProgress {
    background-color: #E8D8C7;
    border: none;
    border-radius: 9px;
    text-align: center;
}

QProgressBar#pourProgress::chunk {
    background-color: #7A5538;
    border-radius: 9px;
}

QLabel#runningWarning {
    color: #9A7557;
}

QPushButton#cancelButton {
    background-color: #FFFDFC;
    color: #A32620;
    border: 2px solid #C66A63;
    border-radius: 18px;
    padding: 9px 18px;
}

QPushButton#cancelButton:hover {
    background-color: #F8E3E0;
    border-color: #B3261E;
}

QPushButton#cancelButton:pressed {
    background-color: #EBC4C0;
}

/* =========================================================
   COMPLETE PAGE
   ========================================================= */
QWidget#completePage {
    background-color: #F8EFE5;
}

QLabel#successIcon {
    background-color: #E5EBDD;
    color: #4F6848;
    border: 1px solid #CAD6C0;
    border-radius: 34px;
    font-size: 34px;
    font-weight: 900;
}

QLabel#completeEyebrow {
    color: #A17D5D;
    font-weight: 800;
    letter-spacing: 2px;
}

QLabel#completeTitle {
    color: #2F1E12;
}

QLabel#completeArtIcon {
    background-color: #FFFDFC;
    border: 1px solid #E1D0BF;
    border-radius: 24px;
    padding: 6px;
}

QLabel#completeArtName {
    color: #7A5538;
    font-weight: 800;
    letter-spacing: 2px;
}

QLabel#completeMessage {
    color: #7C6A5A;
}

QLabel#countdownLabel {
    color: #A38366;
}

QPushButton#homeButton {
    background-color: #3A2616;
    color: #FFFDFC;
    border: 2px solid #3A2616;
    border-radius: 19px;
    padding: 10px 18px;
}

QPushButton#homeButton:hover {
    background-color: #5A3B25;
    border-color: #5A3B25;
}

QPushButton#homeButton:pressed {
    background-color: #2F1E12;
}

/* =========================================================
   STATUS PAGE
   ========================================================= */
QWidget#statusPage {
    background-color: #F8EFE5;
}

QFrame#statusCard {
    background-color: #FFFDFC;
    border: 1px solid #E1D0BF;
    border-radius: 22px;
}

QLabel#statusCardTitle {
    color: #9A7557;
    font-weight: 800;
    letter-spacing: 1px;
}

QLabel#statusCardHint {
    color: #A58A73;
}

QLabel#statusValueGood,
QLabel#statusValueNeutral,
QLabel#statusValueDanger {
    font-weight: 800;
}

QLabel#statusValueGood {
    color: #4F6848;
}

QLabel#statusValueNeutral {
    color: #7A5538;
}

QLabel#statusValueDanger {
    color: #B3261E;
}

/* Backwards-compatible names used by older code paths. */
QLabel#goodStatus {
    color: #4F6848;
    font-weight: 800;
}

QLabel#simulationStatus {
    color: #7A5538;
    font-weight: 800;
}

QLabel#dangerStatus {
    color: #B3261E;
    font-weight: 800;
}

/* =========================================================
   EMERGENCY STOP PAGE
   ========================================================= */
QWidget#emergencyStopPage {
    background-color: #F8EFE5;
}

QFrame#emergencyPanel {
    background-color: #FFF8F6;
    border: 2px solid #D99B95;
    border-radius: 28px;
}

QLabel#estopWarningIcon {
    background-color: #B3261E;
    color: #FFFFFF;
    border-radius: 38px;
    font-size: 40px;
    font-weight: 900;
}

QLabel#estopPageTitle {
    color: #A32620;
}

QLabel#estopMessage {
    color: #5E4940;
}

QLabel#estopStepNumber {
    background-color: #F4DAD7;
    color: #A32620;
    border-radius: 16px;
    font-weight: 800;
}

QLabel#estopStepText {
    color: #6B5148;
}

QPushButton#resetEstopButton {
    background-color: #FFFDFC;
    color: #8F1D18;
    border: 2px solid #B3261E;
    border-radius: 18px;
    padding: 10px 20px;
}

QPushButton#resetEstopButton:hover {
    background-color: #F4DAD7;
}

QPushButton#resetEstopButton:pressed {
    background-color: #EBC4C0;
}

/* =========================================================
   TELEOP LATTE CHALLENGE
   ========================================================= */
QPushButton#levelCard {
    background-color: #FFFDFC;
    border: 2px solid #E1D0BF;
    border-radius: 26px;
    padding: 0px;
}

QPushButton#levelCard:hover {
    border-color: #B89067;
}

QPushButton#levelCard:pressed {
    background-color: #F1E3D4;
    border-color: #7A5538;
}

QLabel#levelEyebrow,
QLabel#gameEyebrow {
    color: #A17D5D;
    letter-spacing: 1px;
}

QLabel#levelName {
    color: #2F1E12;
}

QLabel#levelBest {
    color: #7A5538;
}

QLabel#stepBadge {
    background-color: #3A2616;
    color: #FFFDFC;
    border-radius: 17px;
}

QLabel#stepText {
    color: #5A4636;
}

QLabel#phaseChip {
    border-radius: 19px;
    padding-left: 10px;
    padding-right: 10px;
    letter-spacing: 1px;
}

QLabel#phaseChip[state="todo"] {
    background-color: #F1E5D8;
    color: #A58A73;
}

QLabel#phaseChip[state="active"] {
    background-color: #3A2616;
    color: #FFFDFC;
}

QLabel#phaseChip[state="done"] {
    background-color: #E5EBDD;
    color: #4F6848;
}

QLabel#gameInstruction {
    color: #2F1E12;
}

QLabel#gameTime {
    color: #7A5538;
}

QLabel#meterName {
    color: #9A7557;
    letter-spacing: 1px;
}

QLabel#meterValue {
    color: #3A2616;
}

QLabel#scoreValue {
    color: #2F1E12;
}

QLabel#scoreOutOf {
    color: #A58A73;
}

QLabel#rankLabel {
    color: #7A5538;
    letter-spacing: 2px;
}

QLabel#bestLabel {
    color: #4F6848;
}

QLabel#tipLabel {
    color: #5A4636;
}
"""
