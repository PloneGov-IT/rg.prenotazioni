# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s rg.prenotazioni -t test_prenotazioni_day.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src rg.prenotazioni.testing.RG_PRENOTAZIONI_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/rg/prenotazioni/tests/robot/test_prenotazioni_day.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a PrenotazioniDay
  Given a logged-in site administrator
    and an add PrenotazioniWeek form
   When I type 'My PrenotazioniDay' into the title field
    and I submit the form
   Then a PrenotazioniDay with the title 'My PrenotazioniDay' has been created

Scenario: As a site administrator I can view a PrenotazioniDay
  Given a logged-in site administrator
    and a PrenotazioniDay 'My PrenotazioniDay'
   When I go to the PrenotazioniDay view
   Then I can see the PrenotazioniDay title 'My PrenotazioniDay'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add PrenotazioniWeek form
  Go To  ${PLONE_URL}/++add++PrenotazioniWeek

a PrenotazioniDay 'My PrenotazioniDay'
  Create content  type=PrenotazioniWeek  id=my-prenotazioni_day  title=My PrenotazioniDay

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the PrenotazioniDay view
  Go To  ${PLONE_URL}/my-prenotazioni_day
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a PrenotazioniDay with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the PrenotazioniDay title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
