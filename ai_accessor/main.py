import asyncio
import logging
import logging.config
from dapr.clients.exceptions import DaprInternalError
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from config import load_config, configure_env_variables


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)

kernel = Kernel()


async def main():
    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id='gpt-3.5-turbo',
            service_id='chat-gpt',
        )
    )

    plugin = kernel.add_plugin(
        parent_directory="prompt_templates", plugin_name="DigestPlugin"
    )
    digest_function = plugin["digest"]

    result = await kernel.invoke(
        digest_function,
        input="""Hopes of Gaza ceasefire rise further as Hamas reportedly backs new proposal
Militant group gives initial backing to plan for phased deal after ‘verbal commitments’ from mediators
Israel-Gaza war – live updates
Jason Burke in Jerusalem
Sat 6 Jul 2024 15.59 BST
Share
Hopes for a ceasefire in Gaza have risen further after reports that Hamas has given its initial approval of a new US-backed proposal for a phased deal.

Egyptian officials and representatives of the militant Islamist organisation confirmed Hamas had dropped a key demand that Israel commits to a definitive end to the war before any pause in hostilities, Reuters and the Associated Press reported.

Efforts to secure a ceasefire and hostage release in Gaza have intensified over recent days, with active shuttle diplomacy among Washington, Israel and Qatar, which is leading mediation efforts from Doha, where the exiled Hamas leadership is based.

Observers said any progress was welcome, but pointed out that multiple rounds of negotiations over more than seven months had so far failed to bring success.""",
        amount_of_sentences=str(1),
    )
    print(result)


if __name__ == "__main__":
    logger.info('Starting AI Accessor')
    try:
        configure_env_variables(config.secrets.store_name)
    except DaprInternalError as e:
        logger.error(f'Could not connect to the secrets store. Terminating. {str(e)}')
        raise
    asyncio.run(main())

# semantic_kernel.exceptions.kernel_exceptions.KernelInvokeException, ServiceResponseException, openai.RateLimitError
