import os
import csv
import io
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

if not all([GITHUB_TOKEN, REPO_OWNER, REPO_NAME]):
    raise ValueError("Erro: Certifique-se de que GITHUB_TOKEN, REPO_OWNER e REPO_NAME estão configurados no arquivo .env")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


def calcular_duracao(inicio_str, fim_str):
    """Calcula a diferença em segundos entre duas datas ISO 8601."""
    if not inicio_str or not fim_str:
        return 0
    inicio = datetime.fromisoformat(inicio_str.replace("Z", "+00:00"))
    fim = datetime.fromisoformat(fim_str.replace("Z", "+00:00"))
    return int((fim - inicio).total_seconds())


def extrair_metricas_do_artefato(run_id):
    """Baixa o artefato de testes da API, descompacta e lê o XML do pytest."""
    url = f"{BASE_URL}/actions/runs/{run_id}/artifacts"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return 0, 0

    artifacts = response.json().get("artifacts", [])
    for artifact in artifacts:
        if artifact["name"] == "relatorio-testes":
            download_url = artifact["archive_download_url"]
            
            redirect_res = requests.get(download_url, headers=HEADERS, allow_redirects=False)
            if redirect_res.status_code in [301, 302]:
                s3_url = redirect_res.headers["Location"]
                artifact_res = requests.get(s3_url)
            else:
                artifact_res = redirect_res

            if artifact_res.status_code == 200:
                try:
                    with zipfile.ZipFile(io.BytesIO(artifact_res.content)) as z:
                        xml_content = z.read("resultados_testes.xml")
                        root = ET.fromstring(xml_content)
                        
                        total_tests = int(root.get("tests", 0))
                        failures = int(root.get("failures", 0))
                        return total_tests, failures
                except Exception as e:
                    print(f" Avisando: Falha ao processar XML do run {run_id}: {e}")
    return 0, 0


def coletar_dados_pipeline():
    print(" Buscando execuções do pipeline no GitHub...")
    url_runs = f"{BASE_URL}/actions/runs?per_page=20"
    res_runs = requests.get(url_runs, headers=HEADERS)

    if res_runs.status_code != 200:
        print(f"Erro ao acessar API: {res_runs.status_code} - {res_runs.text}")
        return

    runs = res_runs.json().get("workflow_runs", [])
    dados_finais = []

    for run in runs:
        run_id = run["id"]
        status_workflow = run["conclusion"]
        
        if run["status"] != "completed":
            continue
            
        commit_sha = run["head_sha"]
        commit_msg = run["head_commit"]["message"].split("\n")[0] if run["head_commit"] else "Sem mensagem"
        timestamp = run["created_at"]
        
        workflow_duration = calcular_duracao(run["run_started_at"], run["updated_at"])

        print(f" Processando Run ID {run_id} | Commit: {commit_msg[:30]}...")

        res_jobs = requests.get(run["jobs_url"], headers=HEADERS)
        if res_jobs.status_code == 200:
            jobs = res_jobs.json().get("jobs", [])
            
            test_count, test_failures = extrair_metricas_do_artefato(run_id)

            for job in jobs:
                job_name = job["name"]
                job_duration = calcular_duracao(job["started_at"], job["completed_at"])
                
                job_test_count = test_count if "Testes" in job_name else 0
                job_test_failures = test_failures if "Testes" in job_name else 0

                dados_finais.append({
                    "run_id": run_id,
                    "commit_sha": commit_sha[:7],
                    "commit_message": commit_msg,
                    "status": status_workflow,
                    "workflow_duration": workflow_duration,
                    "job_name": job_name,
                    "job_duration": job_duration,
                    "test_count": job_test_count,
                    "test_failures": job_test_failures,
                    "timestamp": timestamp
                })

    nome_csv = "metricas_pipeline.csv"
    colunas = [
        "run_id", "commit_sha", "commit_message", "status", 
        "workflow_duration", "job_name", "job_duration", 
        "test_count", "test_failures", "timestamp"
    ]

    with open(nome_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(dados_finais)

    print(f"\n Base de dados gerada com sucesso em: '{nome_csv}'!")


if __name__ == "__main__":
    coletar_dados_pipeline()