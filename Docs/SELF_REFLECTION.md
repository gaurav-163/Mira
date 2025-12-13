# Self-Reflection Feature

## Overview
The self-reflection method validates and improves answer quality before presenting to users.

## How It Works

### 1. Answer Generation
First, the system generates an answer using RAG (Retrieval-Augmented Generation).

### 2. Quality Check
The self-reflection mechanism evaluates:
- **Relevance**: Does the answer address the question?
- **Accuracy**: Is the answer based on the provided context?
- **Completeness**: Are all key points covered?

### 3. Improvement
If the answer quality is poor or fair, the system generates an improved version.

## Configuration

### Enable Self-Reflection
Edit `.env` file:
```bash
ENABLE_REFLECTION=true
```

### Performance Impact
- **Disabled** (default): 2-3 second response time
- **Enabled**: 4-6 second response time (adds one extra LLM call)

## Example

**Question**: "What is a data warehouse?"

**Without Reflection**:
```
Answer: A data warehouse stores data.
```

**With Reflection**:
```
ANSWER: A data warehouse is a central repository for an organization's 
historical data, designed to support decision-making processes.

KEY POINTS:
- Built to store and analyze large volumes of data
- Transforms raw data into meaningful information
- Structured for easy retrieval and analysis

ADDITIONAL CONTEXT:
Data warehousing emerged to address limitations of traditional systems...
```

## When to Use

### Enable When:
- Accuracy is critical (research, medical, legal)
- Users need detailed, well-structured answers
- Quality is more important than speed

### Disable When:
- Speed is priority (chatbot, quick lookups)
- Simple questions that don't need validation
- High-traffic applications

## Implementation Details

### Method: `_reflect_on_answer()`
```python
def _reflect_on_answer(self, question: str, answer: str, context: str) -> Dict:
    """Self-reflection: Validate answer quality and relevance"""
    # Creates a quality checker prompt
    # Evaluates: Good/Fair/Poor
    # Returns improved answer if needed
```

### Integration
Self-reflection is automatically applied in `_answer_from_knowledge_base()` when:
1. `ENABLE_REFLECTION=true` in `.env`
2. Knowledge base documents are found
3. RAG chain successfully generates an answer

## Logging

Check logs to see when reflection improves answers:
```bash
tail -f logs/app.log | grep "reflection"
```

Output example:
```
2025-12-10 16:30:45 - service - INFO - Self-reflection: Improved answer generated
2025-12-10 16:30:45 - service - INFO - Using improved answer from self-reflection
```

## Benefits

✅ **Higher Quality**: Catches incomplete or irrelevant answers  
✅ **Better Structure**: Ensures consistent formatting  
✅ **Context Awareness**: Validates answer matches context  
✅ **User Satisfaction**: More accurate, helpful responses  

## Trade-offs

⚠️ **Slower**: Adds 2-3 seconds per question  
⚠️ **More API Calls**: Doubles LLM usage costs  
⚠️ **Still Experimental**: May occasionally over-correct good answers  

## Future Enhancements

- [ ] Selective reflection (only for complex questions)
- [ ] Caching reflection results
- [ ] User feedback loop to improve reflection prompts
- [ ] Confidence scoring
