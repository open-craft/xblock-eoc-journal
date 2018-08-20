API for native mobile frontends
-------------------------------
**Retrieve fixed data for all Course Journal XBlocks in a course:**
```
GET https://<lms_server_url>/api/courses/v1/blocks/?course_id=<course_id>&username=<username>&depth=all&requested_fields=student_view_data
```

Example return value:
```json
{
  ...
  "student_view_data": {
    "display_name": "Course Journal",
    "display_answers": true,
    "display_user_metrics": true,
    "display_key_takeaways": true,
    "key_takeaways_pdf_url": "/path/to/takeaways.pdf",
    "pdf_report_url": "/path/to/report.pdf",
    "pdf_report_link_heading": "PDF Report",
    "pdf_report_link_text": "PDF Report Link"
  },
  ...
}
```

**NOTE**: While the contents of the course journal report located at 
``pdf_report_url`` are different for each user, the URL itself is the 
same, and as such is included in ``student_view_data``.

**Retrieve user-specific data for Course Journal XBlock in a course:**

GET https://<lms_server_url>/courses/<course_id>/xblock/<block_id>/handler/student_view_user_state

```json
{
  "answer_sections": [
    {
      "name": "First Section",
      "questions": [
        {
          "answer": "Not answered yet.",
          "question": "Hello, who are you? What's your name?"
        },
        {
          "answer": "student input",
          "question": "Tell us more about yourself."
        }
      ]
    }
  ],
  "progress": {
    "user": 22,
    "cohort_average": 67
  },
  "proficiency": {
    "user": 44,
    "cohort_average": 32
  }
}
```
