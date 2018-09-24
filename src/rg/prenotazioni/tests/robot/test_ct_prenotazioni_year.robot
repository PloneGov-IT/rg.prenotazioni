# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s rg.prenotazioni -t test_prenotazioni_year.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src rg.prenotazioni.testing.RG_PRENOTAZIONI_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/rg/prenotazioni/tests/robot/test_prenotazioni_year.robot
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

Scenario: As a site administrator I can add a PrenotazioniYear
  Given a logged-in site administrator
    and an add PrenotazioniFolder form
   When I type 'My PrenotazioniYear' into the title field
    and I submit the form
   Then a PrenotazioniYear with the title 'My PrenotazioniYear' has been created

Scenario: As a site administrator I can view a PrenotazioniYear
  Given a logged-in site administrator
    and a PrenotazioniYear 'My PrenotazioniYear'
   When I go to the PrenotazioniYear view
   Then I can see the PrenotazioniYear title 'My PrenotazioniYear'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add PrenotazioniFolder form
  Go To  ${PLONE_URL}/++add++PrenotazioniFolder

a PrenotazioniYear 'My PrenotazioniYear'
  Create content  type=PrenotazioniFolder  id=my-prenotazioni_year  title=My PrenotazioniYear

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the PrenotazioniYear view
  Go To  ${PLONE_URL}/my-prenotazioni_year
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a PrenotazioniYear with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the PrenotazioniYear title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
