import os
from unittest.mock import patch, MagicMock
from core.llm_generator.llm_generator import LLMGenerator
from core.llm_generator import prompts

def test_suggested_questions_env_config():
    """
    Test that LLMGenerator uses the values from environment variables
    for suggested questions generation.
    """
    custom_prompt = "Custom technical prompt"
    custom_max_tokens = 999
    custom_temp = 0.5

    # We need to reload or patch the constants in the prompts module
    # because they are evaluated at import time.
    with patch.dict(os.environ, {
        "SUGGESTED_QUESTIONS_PROMPT": custom_prompt,
        "SUGGESTED_QUESTIONS_MAX_TOKENS": str(custom_max_tokens),
        "SUGGESTED_QUESTIONS_TEMPERATURE": str(custom_temp)
    }):
        # Force re-evaluation of environment variables in prompts.py
        import importlib
        importlib.reload(prompts)
        
        # Patch LLMGenerator to use the reloaded constants
        with patch('core.llm_generator.llm_generator.SUGGESTED_QUESTIONS_MAX_TOKENS', prompts.SUGGESTED_QUESTIONS_MAX_TOKENS), \
             patch('core.llm_generator.llm_generator.SUGGESTED_QUESTIONS_TEMPERATURE', prompts.SUGGESTED_QUESTIONS_TEMPERATURE), \
             patch('core.llm_generator.output_parser.suggested_questions_after_answer.SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT', prompts.SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT):
            
            assert prompts.SUGGESTED_QUESTIONS_MAX_TOKENS == custom_max_tokens
            assert prompts.SUGGESTED_QUESTIONS_TEMPERATURE == custom_temp
            assert prompts.SUGGESTED_QUESTIONS_AFTER_ANSWER_INSTRUCTION_PROMPT == custom_prompt

            # Verify LLMGenerator uses these values when calling invoke_llm
            tenant_id = "test_tenant"
            histories = "test histories"
            
            with patch('core.llm_generator.llm_generator.ModelManager') as mock_model_manager, \
                 patch('core.llm_generator.llm_generator.SuggestedQuestionsAfterAnswerOutputParser') as mock_parser:
                
                mock_model_instance = MagicMock()
                mock_model_manager.return_value.get_default_model_instance.return_value = mock_model_instance
                mock_parser.return_value.get_format_instructions.return_value = custom_prompt
                
                LLMGenerator.generate_suggested_questions_after_answer(tenant_id, histories)
                
                # Check if invoke_llm was called with the correct parameters
                args, kwargs = mock_model_instance.invoke_llm.call_args
                assert kwargs['model_parameters']['max_tokens'] == custom_max_tokens
                assert kwargs['model_parameters']['temperature'] == custom_temp
