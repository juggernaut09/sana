## core_offerings
* core_offerings
  - action_core_offerings

## just faq
* faq
  - respond_faq

## impact_industries
* impact_industries
  - action_impact_industries

## recent_stories
* recent_stories
  - action_recent_stories


## contact_us
* contact_us
  - utter_can_do
  - contact_form
  - form{"name": "contact_form"}
  - form{"name": null}

## contact_us+canthelp+affirm
* contact_us
  - utter_can_do
  - contact_form
  - form{"name": "contact_form"}
* canthelp
  - utter_canthelp
  - utter_ask_continue
* affirm
  - utter_great
  - contact_form
  - form{"name": null}

## contact_us+canthelp+deny
* contact_us
  - utter_can_do
  - contact_form
  - form{"name": "contact_form"}
* canthelp
  - utter_canthelp
  - utter_ask_continue
* deny
  - utter_thumbsup
  - action_deactivate_form
  - form{"name": null}

## contact_us+explain+affirm
* contact_us
  - utter_can_do
  - contact_form
  - form{"name": "contact_form"}
* explain
  - action_explain_contact_form
  - utter_ask_continue
* affirm
  - utter_great
  - contact_form
  - form{"name": null}

## contact_us+explain+deny
* contact_us
  - utter_can_do
  - contact_form
  - form{"name": "contact_form"}
* explain
  - action_explain_contact_form
  - utter_ask_continue
* deny
  - utter_thumbsup
  - action_deactivate_form
  - form{"name": null}
