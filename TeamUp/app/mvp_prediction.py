from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
load_dotenv()

def get_mvp(scoreboard):
    llm= ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
    )

    class CricketPerformance(BaseModel):
        top_performers: list[str] = Field(
            description="List of top 5 performers of the day based on their stats. Dont use any names more than once in the list."),
        top_performers_runs: list[int] = Field(
            description="List of top 5 performers' runs scored."),
        top_performers_wickets: list[int] = Field(
            description="List of top 5 performers' wickets taken."),
        top_performers_strikeRate: list[float] = Field(
            description="List of top 5 performers' batting strike rates."),
        top_performers_economy: list[float] = Field(
            description="List of top 5 performers' bowling economy rates."),
        mvp: str = Field(
            description="Name of the player who is the Man of the Match based on performance.")

    parser = PydanticOutputParser(pydantic_object=CricketPerformance)

    prompt=PromptTemplate(
        template='''
        You are a great sports analyst. From the given scoreboard of a cricket match, provide me the top 5 performers of the day.
        Also provide the name of the MAN OF THE MATCH according to the performance of the player with his stats.
        Dont use any names more than once in the top performers list.
        Follow the below format to provide the output:
        \n
        {format_instruction},

        \n\n\n
        Scoreboard: 
        {scoreboard}
        \n\n\n''',
        input_variables=['scoreboard'],
        partial_variables={
            "format_instruction": parser.get_format_instructions()
        }
    )

    chain=prompt | llm | parser
    result=chain.invoke({"scoreboard": scoreboard})
    return dict(result)