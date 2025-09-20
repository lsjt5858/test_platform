import click
import os
import shutil
import subprocess
import sys

@click.group()
def cli():
    """🐻 Bears Test Platform - Unified Test Automation Engine"""
    pass

@cli.command()
@click.argument('domain')
def new(domain):
    """🚀 Generate a new test domain template (e.g., 'bears new payment')"""
    template_path = "cli/templates/bears_domain_template"  
    target_path = f"test/domain/{domain}"

    if not os.path.exists(target_path):
        shutil.copytree(template_path, target_path)
        print(f"✅ Created new domain: {domain} under test/domain/")
    else:
        print(f"❌ Domain '{domain}' already exists. Aborted.")

@cli.command()
def version():
    """🔖 Show Bears Test Platform version"""
    print("Bears Test Platform v0.1.0")

# 仅使用 Allure 生成报告
@cli.command()
@click.argument('test_type', type=click.Choice(['api', 'ui', 'biz', 'all'], case_sensitive=False))
@click.option('--domain', required=True, help='Test domain to run (e.g., enterprise)')
@click.option('--k', 'kexpr', default=None, help='pytest -k expression to filter tests')
@click.option('-v', '--verbose', is_flag=True, help='Verbose pytest output')
@click.option('--report-dir', default='test/reports/latest', show_default=True, help='Final Allure report output directory (will be overwritten each run)')
def run(test_type, domain, kexpr, verbose, report_dir):
    """🏃 Run tests and generate Allure report, e.g. 'bears run api --domain=enterprise'"""
    base_dir = os.path.join('test', 'domain', domain)
    if not os.path.isdir(base_dir):
        click.echo(f"❌ Domain not found: {base_dir}")
        sys.exit(1)

    # 清空最终报告目录，确保只保留本次报告
    try:
        if os.path.exists(report_dir):
            shutil.rmtree(report_dir)
        os.makedirs(report_dir, exist_ok=True)
    except Exception as e:
        click.echo(f"❌ Failed to prepare report directory '{report_dir}': {e}")
        sys.exit(1)

    # 临时 Allure 结果目录（与最终目录同级，避免 --clean 清理冲突）
    results_dir = os.path.join(os.path.dirname(report_dir), '.allure_results_tmp')
    try:
        if os.path.exists(results_dir):
            shutil.rmtree(results_dir)
        os.makedirs(results_dir, exist_ok=True)
    except Exception as e:
        click.echo(f"❌ Failed to prepare allure results directory '{results_dir}': {e}")
        sys.exit(1)

    targets = []
    ttype = test_type.lower()
    if ttype == 'all':
        for t in ['api', 'ui', 'biz']:
            tdir = os.path.join(base_dir, t)
            if os.path.isdir(tdir):
                targets.append(tdir)
        if not targets:
            targets = [base_dir]
    else:
        tdir = os.path.join(base_dir, ttype)
        if os.path.isdir(tdir):
            targets = [tdir]
        else:
            click.echo(f"⚠️ Subdirectory '{ttype}' not found under {base_dir}, fallback to domain root.")
            targets = [base_dir]

    cmd = ['pytest'] + targets
    if kexpr:
        cmd += ['-k', kexpr]
    if verbose:
        cmd += ['-v']
    cmd += ['--color=yes', '--alluredir', results_dir]

    click.echo(f"🏃 Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=False)

        allure_bin = shutil.which('allure')
        if allure_bin:
            gen_cmd = [allure_bin, 'generate', results_dir, '-o', report_dir, '--clean']
            click.echo(f"🧪 Generating Allure report: {' '.join(gen_cmd)}")
            gen_res = subprocess.run(gen_cmd, check=False)
            if gen_res.returncode != 0:
                click.echo("⚠️ Failed to generate Allure HTML report. Please ensure 'allure' CLI is properly installed.")
            else:
                # 生成成功后删除临时结果目录，只保留最终报告
                try:
                    shutil.rmtree(results_dir)
                except Exception:
                    pass
        else:
            click.echo("ℹ️ 'allure' CLI not found. Skipping HTML generation. Install via: brew install allure")
            click.echo(f"   Allure results are available at: {results_dir}")

        sys.exit(result.returncode)
    except FileNotFoundError:
        click.echo("❌ 'pytest' command not found. Please ensure pytest is installed and available in PATH.")
        sys.exit(1)

if __name__ == '__main__':
    cli()
