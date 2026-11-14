from langchain_core.tools import tool
from retrieval.vector_store import create_vb
from bs4 import BeautifulSoup
import statistics
import pandas as pd

@tool
def extract_table(table_document: dict) -> dict:
    """
    Extract a table from an retrieved document
    and convert it into structured headers and rows.
    """

    content = table_document.get("content", "")
    metadata = table_document.get("metadata", {})

    if metadata.get("content_type") != "table":
        return {"error": "The provided document is not a table."}

    soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table")

    if not table:
        return {"error": "No table found in the provided document."}
    
    rows = table.find_all("tr")
    if not rows:
        return {"error": "The table is empty."}

    header_cells = rows[0].find_all(["th", "td"])
    headers = [
        cell.get_text(strip=True)
        for cell in header_cells
    ]

    data_rows = []
    for row in rows[1:]:
        cells = [
            cell.get_text(strip=True)
            for cell in row.find_all(["td", "th"])
        ]
        if not cells:
            continue
        data_rows.append(dict(zip(headers, cells)))

    return {
        "headers": headers,
        "rows": data_rows,
        "file_name": metadata.get("file_name"),
        "table_id": metadata.get("chunk_id")
    }


@tool
def document_comparison(query: str,documents: list[dict]) -> dict:
    """
    Compare retrieved evidence from multiple documents.

    Args:
        query: The user's comparison question.
        documents: Retrieved documents with their content and metadata.
    """

    comparison_data = {}

    for doc in documents:
        metadata = doc.get("metadata", {})
        file_name = metadata.get("file_name", "unknown")

        if file_name not in comparison_data:
            comparison_data[file_name] = []

        comparison_data[file_name].append(
            doc.get("content", "")
        )

    return {
        "query": query,
        "documents": [
            {
                "document": file_name,
                "evidence": evidence
            }
            for file_name, evidence in comparison_data.items()
        ]
    }

@tool
def calculator(op:str , values:list[float])->str:

    """
    Perform accurate mathematical and statistical calculations.

    Supported operations:
    - add
    - subtract
    - multiply
    - divide
    - percentage_of
    - percentage_change
    - average
    - ratio
    - sum
    - min
    - max
    - variance
    - standard_deviation

    Args:
        operation: The mathematical operation to perform.
        values: Numerical values used in the calculation.

    Notes:
        subtract: first value - second value
        divide: first value / second value
        percentage_of: percentage, total
        percentage_change: old_value, new_value
        ratio: first value, second value
    """

    if not values:
        raise ValueError("at least one numerical is required")

    values =[float(v) for v in values]

    if op == "add": res = sum(values)

    elif op == "subtract":
        if len(values)!=2: raise ValueError("subtract requires exactly two values")
        res = values[0] -values[1]

    elif op =="multiply":
        res =1
        for v in values:
            res *= v

    elif op =="divide":
        if len(values)!=2:
            raise ValueError("subtract requires exactly two values")
        if values[1] == 0:
            raise ValueError("division by zero is not allowed")
        res = values[0] / values[1]

    elif op =="percentage_of":
        if len(values)!=2:
            raise ValueError("percentage_of requires percentage and total")
        res =(values[0]/100) *values[1]

    elif op =="average":
        res =sum(values)/len(values)

    elif op =="ratio":
        if len(values)!=2:
            raise ValueError("ratio requires exactly two values")
        if values[1] == 0:
            raise ValueError("ratio by zero is not allowed")
        res = values[0] / values[1]

    elif op =="sum":
        res =sum(values)

    elif op =="min":
        res =min(values)

    elif op =="max":
        res=max(values)

    elif op == "variance":
            if len(values) < 2:
                raise ValueError("variance requires at least two values")
            res = statistics.pvariance(values)

    elif op == "standard_deviation":
        if len(values) < 2:
            raise ValueError("standard deviation requires at least two values")
        res = statistics.pstdev(values)

    else:
        return {
            "error": f"Unsupported operation: {op}"
        }

    return res


@tool
def data_analysis(data: list[dict]) -> dict:
    """
    Perform structured statistical analysis on tabular data.
    Args:
        data: A list of dictionaries representing rows.
              Each row should contain numerical metrics
              and optionally a model/name identifier.
    """

    if not data: return {"error": "No data provided"}

    df = pd.DataFrame(data)
    if df.empty: return {"error": "The dataset is empty"}

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty: return {"error": "No numerical columns found"}

    statistics = numeric_df.describe().to_dict()
    averages = numeric_df.mean().to_dict()

    highest = numeric_df.max().to_dict()
    lowest = numeric_df.min().to_dict()

    correlation = numeric_df.corr().to_dict()

    ranking = []

    if "model" in df.columns:
        ranked_df = df.copy()
        metrics = numeric_df.columns.tolist()

        ranked_df["overall_score"] = (
            ranked_df[metrics].mean(axis=1)
        )
        ranked_df = ranked_df.sort_values(
            by="overall_score",
            ascending=False
        )
        ranking = ranked_df[
            ["model", "overall_score"]
        ].to_dict(orient="records")

    return {
        "statistics": statistics,
        "averages": averages,
        "highest": highest,
        "lowest": lowest,
        "correlation": correlation,
        "ranking": ranking
    }

@tool
def retrieve_more_evidence(query:str)->str:
    """
    Request additional evidence from the Retriever Agent.

    Use this tool when the currently available evidence
    is insufficient to answer the user's question.

    Args:
        query: A specific query describing the missing evidence.
    """

    return (
        f"MORE_EVIDENCE_REQUIRED: {query}"
    )


tools= [retrieve_more_evidence,
 data_analysis,
 calculator,
 document_comparison,
 extract_table
]