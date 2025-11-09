import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.graph import create_graph, MCP_SERVER_CLIENT, GRAPH_MEMORY
from configs.config import SMTP_CONFIG
from configs.logger import LOGGER


class NotificationRequest(BaseModel):
    subject: str
    message: str
    session_id: str


notification_router = APIRouter()


@notification_router.post(
    "/notifications",
    summary="Trigger graph and send results to Gmail"
)
async def send_notification(request: NotificationRequest):
    config = {
        "configurable": {"thread_id": request.session_id},
        "checkpoint": GRAPH_MEMORY,
    }
    try:
        async with MCP_SERVER_CLIENT.session("shopify") as shopify_session:
            agent = await create_graph(shopify_session)
            result = None
            async for name, mode, chunk in agent.astream(
                    {"messages": request.message + " Remove all Markdown and generate result in HTML format ONLY with some CSS."},
                    subgraphs=True,
                    config=config,
                    stream_mode=["custom", "values"]
            ):
                if mode == "values":
                    result = next(iter(chunk.values()))
        if not result:
            raise HTTPException(status_code=500, detail="No result from graph invocation.")

        # Only send the last message's content
        last_message_content = None
        if isinstance(result, list) and result:
            # If result is a list of messages, get the last one's content
            last = result[-1]
            last_message_content = getattr(last, 'content', str(last))
        elif hasattr(result, 'content'):
            last_message_content = str(result.content)
        else:
            last_message_content = str(result)

        subject = request.subject
        msg = MIMEMultipart()
        msg["From"] = SMTP_CONFIG.sender_email
        msg["To"] = SMTP_CONFIG.receiver_email
        msg["Subject"] = subject
        # Attach as HTML instead of plain text
        msg.attach(MIMEText(last_message_content, "html"))
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_CONFIG.sender_email, SMTP_CONFIG.password)
                server.sendmail(SMTP_CONFIG.sender_email, SMTP_CONFIG.receiver_email, msg.as_string())
        except Exception as e:
            LOGGER.error(f"Failed to send email: {e}")
            raise HTTPException(status_code=500, detail="Failed to send email.")
        return {"status": "success", "detail": "Notification sent and email delivered."}
    except Exception as ex:
        LOGGER.error(f"Error in notification endpoint: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))
