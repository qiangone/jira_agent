import requests
import os
from dotenv import load_dotenv

load_dotenv()

CR_API_URL   = os.getenv("CR_API_URL")
CR_API_TOKEN = os.getenv("CR_API_TOKEN")


class CRClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {CR_API_TOKEN}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
        }

    def create_cr(self,
                  ticket_ref: str,
                  prod_deployment_ticket_ref: str,
                  schedule_start_time: str,
                  implement_plan_confluence: str,
                  # Component Release fields (optional for DB release)
                  artifact_id: str = None,
                  version_num: str = None,
                  rollback_version_num: str = None,
                  # DB Release fields (optional for Component release)
                  restart_component_artifact_id: str = None,
                  ) -> dict:

        payload = {
            "ticketRef":               ticket_ref,
            "prodDeploymentTicketRef": prod_deployment_ticket_ref,
            "scheduleStartTime":       schedule_start_time,
            "implementPlanConfluence": implement_plan_confluence,
        }

        # Only include fields that are provided
        if artifact_id:
            payload["artifactId"] = artifact_id
        if version_num:
            payload["versionNum"] = version_num
        if rollback_version_num:
            payload["rollbackVersionNum"] = rollback_version_num
        if restart_component_artifact_id:
            payload["restartComponentArtifactId"] = restart_component_artifact_id

        # test only
        print(f"sent to cr creator:{payload}")
        cr_id='CRN00001'
        data=''

        # r = requests.post(
        #     f"{CR_API_URL}/cr",
        #     headers=self.headers,
        #     json=payload,
        # )
        # r.raise_for_status()
        # data = r.json()

        # cr_id = (
        #     data.get("id") or
        #     data.get("crId") or
        #     data.get("cr_id") or
        #     data.get("changeRequestId")
        # )
        if not cr_id:
            raise ValueError(f"CR created but no ID found in response: {data}")

        return {"cr_id": str(cr_id)}

    
