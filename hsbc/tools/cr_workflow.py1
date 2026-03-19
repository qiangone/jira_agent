import os
from dotenv import load_dotenv
from tools.cr_client import CRClient
from tools.jira import JiraClient

load_dotenv()

cr   = CRClient()
jira = JiraClient()

# ── Configure these to match your Jira instance ───────────────
CR_JIRA_CUSTOM_FIELD  = os.getenv("CR_JIRA_CUSTOM_FIELD", "customfield_xxxxx")
CR_JIRA_TRANSITION    = os.getenv("CR_JIRA_TRANSITION", "In Progress")


def _post_cr_jira_update(ticket_ref: str, cr_id: str,
                         extra_comment_lines: list[str]) -> dict:
    """Shared post-CR steps: update custom field, transition, add comment."""
    errors = []

    try:
        jira.update_issue(
            issue_key=ticket_ref,
            custom_fields={CR_JIRA_CUSTOM_FIELD: cr_id},
        )
    except Exception as e:
        errors.append(f"Custom field update failed: {e}")

    try:
        jira.transition_issue(issue_key=ticket_ref, transition_name=CR_JIRA_TRANSITION)
    except Exception as e:
        errors.append(f"Status transition failed: {e}")

    try:
        comment = "\n".join(["CR successfully created.", f"CR ID: {cr_id}"] + extra_comment_lines)
        jira.add_comment(issue_key=ticket_ref, comment=comment)
    except Exception as e:
        errors.append(f"Comment failed: {e}")

    return {
        "cr_id":        cr_id,
        "jira_updated": ticket_ref,
        "warnings":     errors if errors else None,
    }


def create_component_cr(
    ticket_ref: str,
    prod_deployment_ticket_ref: str,
    schedule_start_time: str,
    implement_plan_confluence: str,
    artifact_id: str,
    version_num: str,
    rollback_version_num: str,
) -> dict:
    """Component Release: create CR then update Jira."""
    cr_result = cr.create_cr(
        ticket_ref=ticket_ref,
        prod_deployment_ticket_ref=prod_deployment_ticket_ref,
        schedule_start_time=schedule_start_time,
        implement_plan_confluence=implement_plan_confluence,
        artifact_id=artifact_id,
        version_num=version_num,
        rollback_version_num=rollback_version_num,
    )
    cr_id = cr_result["cr_id"]

    comment_lines = [
        f"Release Type: Component Release",
        f"Prod Deployment Ticket: {prod_deployment_ticket_ref}",
        f"Scheduled Start: {schedule_start_time}",
        f"Artifact: {artifact_id}  v{version_num} (rollback: {rollback_version_num})",
        f"Implementation Plan: {implement_plan_confluence}",
    ]
    return _post_cr_jira_update(ticket_ref, cr_id, comment_lines)


def create_db_cr(
    ticket_ref: str,
    prod_deployment_ticket_ref: str,
    schedule_start_time: str,
    implement_plan_confluence: str,
    restart_component_artifact_id: str,
) -> dict:
    """DB Release: create CR then update Jira."""
    cr_result = cr.create_cr(
        ticket_ref=ticket_ref,
        prod_deployment_ticket_ref=prod_deployment_ticket_ref,
        schedule_start_time=schedule_start_time,
        implement_plan_confluence=implement_plan_confluence,
        # DB release does not have artifact_id / version_num / rollback_version_num
        artifact_id=None,
        version_num=None,
        rollback_version_num=None,
        restart_component_artifact_id=restart_component_artifact_id,
    )
    cr_id = cr_result["cr_id"]

    comment_lines = [
        f"Release Type: DB Release",
        f"Prod Deployment Ticket: {prod_deployment_ticket_ref}",
        f"Scheduled Start: {schedule_start_time}",
        f"Restart Component Artifact ID: {restart_component_artifact_id}",
        f"Implementation Plan: {implement_plan_confluence}",
    ]
    return _post_cr_jira_update(ticket_ref, cr_id, comment_lines)