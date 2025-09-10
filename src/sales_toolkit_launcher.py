#!/usr/bin/env python3
"""
Sales Toolkit Launcher - Integrated Revenue Generation Tools
Combines ROI Calculator, Rapid Assessment, and Proposal Generator
For Chilean E-commerce Consulting
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Optional
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich import print as rprint

# Import the three critical tools
from enhanced_roi_calculator import EnhancedROICalculator, ChileanMarketConstants
from rapid_assessment_tool import RapidAssessmentTool
from automated_proposal_generator import AutomatedProposalGenerator


class SalesToolkitLauncher:
    """Integrated launcher for revenue-generating consulting tools"""
    
    def __init__(self):
        self.console = Console()
        self.roi_calculator = EnhancedROICalculator()
        self.assessment_tool = RapidAssessmentTool()
        self.proposal_generator = AutomatedProposalGenerator()
        
        # Storage for session data
        self.session_data = {
            'client_data': {},
            'assessment_results': {},
            'roi_analysis': {},
            'proposal_data': {}
        }
        
        # Session tracking
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = f"output/session_{self.session_id}"
        
    def run(self):
        """Main entry point for the toolkit"""
        self.console.clear()
        self._display_welcome()
        
        while True:
            choice = self._display_main_menu()
            
            if choice == '1':
                self._quick_sales_workflow()
            elif choice == '2':
                self._run_assessment()
            elif choice == '3':
                self._run_roi_calculator()
            elif choice == '4':
                self._generate_proposal()
            elif choice == '5':
                self._view_results()
            elif choice == '6':
                self._export_all()
            elif choice == '7':
                self._load_session()
            elif choice == '8':
                break
            else:
                self.console.print("[red]Opción inválida. Intente nuevamente.[/red]")
    
    def _display_welcome(self):
        """Display welcome screen"""
        welcome_text = """
        [bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]
        [bold white]    SALES TOOLKIT - E-COMMERCE CONSULTING CHILE[/bold white]
        [cyan]         Herramientas Integradas de Venta v2.0[/cyan]
        [bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]
        
        [yellow]✨ 3 Herramientas Críticas:[/yellow]
        [green]1.[/green] Evaluación Rápida (15 min) - Califica prospectos
        [green]2.[/green] Calculadora ROI Avanzada - Cierra ventas
        [green]3.[/green] Generador de Propuestas - 30 min vs 4 horas
        
        [dim]Session ID: {self.session_id}[/dim]
        """
        
        self.console.print(Panel(welcome_text, expand=False))
    
    def _display_main_menu(self) -> str:
        """Display main menu and get user choice"""
        menu = """
        [bold yellow]MENÚ PRINCIPAL[/bold yellow]
        
        [cyan]Flujos Completos:[/cyan]
        [bold]1.[/bold] 🚀 Flujo Rápido de Venta (Assessment → ROI → Propuesta)
        
        [cyan]Herramientas Individuales:[/cyan]
        [bold]2.[/bold] 📋 Ejecutar Evaluación Rápida (15 min)
        [bold]3.[/bold] 💰 Calcular ROI Detallado
        [bold]4.[/bold] 📄 Generar Propuesta Profesional
        
        [cyan]Gestión:[/cyan]
        [bold]5.[/bold] 👁️  Ver Resultados Actuales
        [bold]6.[/bold] 💾 Exportar Todo (PDF, Excel, PowerPoint)
        [bold]7.[/bold] 📂 Cargar Sesión Anterior
        [bold]8.[/bold] 🚪 Salir
        """
        
        self.console.print(menu)
        return Prompt.ask("\n[bold cyan]Seleccione una opción[/bold cyan]")
    
    def _quick_sales_workflow(self):
        """Execute complete sales workflow"""
        self.console.print("\n[bold green]🚀 INICIANDO FLUJO RÁPIDO DE VENTA[/bold green]\n")
        
        # Step 1: Collect basic client info
        self.console.print("[yellow]Paso 1/4: Información del Cliente[/yellow]")
        self._collect_client_data()
        
        # Step 2: Run rapid assessment
        self.console.print("\n[yellow]Paso 2/4: Evaluación Rápida (15 min)[/yellow]")
        self._run_assessment()
        
        # Step 3: Calculate ROI
        self.console.print("\n[yellow]Paso 3/4: Análisis de ROI[/yellow]")
        self._run_roi_calculator()
        
        # Step 4: Generate proposal
        self.console.print("\n[yellow]Paso 4/4: Generación de Propuesta[/yellow]")
        self._generate_proposal()
        
        # Summary
        self._display_workflow_summary()
        
        # Export options
        if Confirm.ask("\n¿Desea exportar todos los documentos?"):
            self._export_all()
    
    def _collect_client_data(self):
        """Collect basic client information"""
        self.console.print("\n[cyan]INFORMACIÓN DEL CLIENTE[/cyan]")
        
        self.session_data['client_data'] = {
            'company_name': Prompt.ask("Nombre de la empresa"),
            'contact_name': Prompt.ask("Nombre del contacto"),
            'email': Prompt.ask("Email"),
            'phone': Prompt.ask("Teléfono"),
            'industry': Prompt.ask("Industria", choices=['Retail', 'Wholesale', 'Servicios', 'Manufactura']),
            'website': Prompt.ask("Sitio web (opcional)", default="")
        }
        
        self.console.print("[green]✓ Información del cliente guardada[/green]")
    
    def _run_assessment(self):
        """Run rapid assessment tool"""
        self.console.print("\n[cyan]EVALUACIÓN RÁPIDA - 15 MINUTOS[/cyan]")
        self.console.print("[dim]Responda las siguientes preguntas para evaluar la oportunidad[/dim]\n")
        
        responses = {}
        
        # Basic business questions
        self.console.print("[yellow]📊 Información del Negocio:[/yellow]")
        responses['b1'] = IntPrompt.ask("Facturación anual en CLP", default=500000000)
        responses['b2'] = IntPrompt.ask("Órdenes mensuales promedio", default=1000)
        responses['b3'] = IntPrompt.ask("Empleados en operaciones e-commerce", default=5)
        responses['b4'] = Prompt.ask("Industria", choices=['Retail', 'Wholesale', 'Servicios', 'Manufactura'], default='Retail')
        
        # Technology assessment
        self.console.print("\n[yellow]💻 Evaluación Tecnológica:[/yellow]")
        responses['t1'] = Prompt.ask("Plataforma e-commerce", 
                                     choices=['WooCommerce', 'Shopify', 'Magento', 'PrestaShop', 'Propia', 'Otra'],
                                     default='WooCommerce')
        responses['t2'] = Confirm.ask("¿Tiene integración automática con ERP?", default=False)
        responses['t3'] = ['Defontana'] if Confirm.ask("¿Usa Defontana?", default=True) else ['Excel']
        responses['t4'] = IntPrompt.ask("Nivel de automatización (1-10)", default=3, min_value=1, max_value=10)
        
        # Operations assessment
        self.console.print("\n[yellow]⚙️ Evaluación Operacional:[/yellow]")
        responses['o1'] = IntPrompt.ask("Tiempo promedio para procesar una orden (minutos)", default=15)
        responses['o2'] = IntPrompt.ask("Porcentaje de órdenes con errores", default=5)
        responses['o3'] = IntPrompt.ask("Horas diarias en tareas operativas repetitivas", default=8)
        responses['o4'] = Confirm.ask("¿Tienen procesos documentados?", default=False)
        responses['o5'] = Prompt.ask("Frecuencia de quiebres de stock",
                                     choices=['Diariamente', 'Semanalmente', 'Mensualmente', 'Raramente'],
                                     default='Semanalmente')
        
        # Integration assessment
        self.console.print("\n[yellow]🔗 Evaluación de Integraciones:[/yellow]")
        responses['i1'] = ['Transbank', 'Webpay'] if Confirm.ask("¿Usa Transbank/Webpay?", default=True) else []
        responses['i2'] = ['Chilexpress'] if Confirm.ask("¿Usa Chilexpress?", default=True) else []
        responses['i3'] = ['No vendo en marketplaces'] if not Confirm.ask("¿Vende en marketplaces?", default=False) else ['MercadoLibre']
        responses['i4'] = Confirm.ask("¿Sincroniza inventario automáticamente entre canales?", default=False)
        
        # Pain points
        self.console.print("\n[yellow]⚠️ Identificación de Problemas:[/yellow]")
        responses['p2'] = IntPrompt.ask("Pérdida mensual estimada por ineficiencias (CLP)", default=5000000)
        responses['p3'] = IntPrompt.ask("Urgencia para resolver problemas (1-10)", default=8, min_value=1, max_value=10)
        
        # Growth plans
        self.console.print("\n[yellow]📈 Planes de Crecimiento:[/yellow]")
        responses['g1'] = IntPrompt.ask("Objetivo de crecimiento próximos 12 meses (%)", default=50)
        responses['g2'] = Confirm.ask("¿Tiene presupuesto asignado para mejoras?", default=True)
        responses['g3'] = Prompt.ask("Timeline ideal para implementar mejoras",
                                     choices=['Inmediato', '1-3 meses', '3-6 meses', '6-12 meses'],
                                     default='1-3 meses')
        
        # Run assessment
        with self.console.status("[bold green]Analizando respuestas..."):
            self.session_data['assessment_results'] = self.assessment_tool.conduct_assessment(responses)
        
        # Display results
        self._display_assessment_results()
    
    def _run_roi_calculator(self):
        """Run ROI calculator with Chilean specifics"""
        self.console.print("\n[cyan]CALCULADORA DE ROI - MERCADO CHILENO[/cyan]")
        
        # Use data from assessment if available
        if self.session_data.get('assessment_results'):
            # Extract data from assessment
            profile = self.session_data['assessment_results'].get('company_profile', {})
            annual_revenue = profile.get('monthly_revenue_clp', 0) * 12
            monthly_orders = profile.get('monthly_orders', 1000)
        else:
            # Collect manually
            annual_revenue = IntPrompt.ask("Facturación anual (CLP)", default=500000000)
            monthly_orders = IntPrompt.ask("Órdenes mensuales", default=1000)
        
        # Collect cost data
        self.console.print("\n[yellow]💰 Costos Operacionales Mensuales (CLP):[/yellow]")
        inputs = {
            'annual_revenue_clp': annual_revenue,
            'monthly_orders': monthly_orders,
            'avg_order_value_clp': annual_revenue / (monthly_orders * 12) if monthly_orders > 0 else 50000,
            'labor_costs_clp': IntPrompt.ask("Costos de personal", default=3500000),
            'shipping_costs_clp': IntPrompt.ask("Costos de envío", default=2000000),
            'platform_fees_clp': IntPrompt.ask("Comisiones de plataformas", default=1200000),
            'error_costs_clp': IntPrompt.ask("Costos por errores", default=500000),
            'inventory_costs_clp': IntPrompt.ask("Costos de inventario", default=1500000),
            'investment_clp': IntPrompt.ask("Inversión en consultoría", default=18000000),
            'industry': self.session_data.get('client_data', {}).get('industry', 'Retail'),
            'current_platforms': ['transbank', 'webpay', 'bsale'],
            'conversion_rate': 0.023
        }
        
        # Calculate ROI
        with self.console.status("[bold green]Calculando ROI con simulación Monte Carlo..."):
            self.session_data['roi_analysis'] = self.roi_calculator.calculate_roi(inputs)
        
        # Display results
        self._display_roi_results()
    
    def _generate_proposal(self):
        """Generate professional proposal"""
        self.console.print("\n[cyan]GENERADOR DE PROPUESTAS PROFESIONALES[/cyan]")
        
        # Check prerequisites
        if not self.session_data.get('client_data'):
            self.console.print("[red]⚠️ Primero debe ingresar información del cliente[/red]")
            self._collect_client_data()
        
        if not self.session_data.get('assessment_results'):
            if Confirm.ask("No hay evaluación. ¿Desea ejecutar una evaluación rápida?"):
                self._run_assessment()
        
        if not self.session_data.get('roi_analysis'):
            if Confirm.ask("No hay análisis ROI. ¿Desea calcular ROI?"):
                self._run_roi_calculator()
        
        # Select proposal options
        template_type = Prompt.ask(
            "Tipo de propuesta",
            choices=['executive', 'detailed', 'quick'],
            default='executive'
        )
        
        package_type = Prompt.ask(
            "Paquete de servicios",
            choices=['starter', 'professional', 'enterprise', 'custom'],
            default='professional'
        )
        
        # Generate proposal
        with self.console.status("[bold green]Generando propuesta profesional..."):
            self.session_data['proposal_data'] = self.proposal_generator.generate_proposal(
                client_data=self.session_data.get('client_data', {}),
                assessment_results=self.session_data.get('assessment_results', {}),
                roi_analysis=self.session_data.get('roi_analysis', {}),
                template_type=template_type,
                package_type=package_type
            )
        
        self.console.print("[green]✓ Propuesta generada exitosamente[/green]")
        
        # Display summary
        self._display_proposal_summary()
    
    def _display_assessment_results(self):
        """Display assessment results summary"""
        results = self.session_data.get('assessment_results', {})
        
        if not results:
            self.console.print("[red]No hay resultados de evaluación disponibles[/red]")
            return
        
        # Create summary table
        table = Table(title="Resultados de Evaluación Rápida", show_header=True)
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="white")
        
        # Maturity level
        maturity = results.get('maturity_level', {})
        table.add_row("Nivel de Madurez", f"[bold]{maturity.get('level', 'N/A')}[/bold]")
        table.add_row("Puntaje General", f"{maturity.get('score', 0):.1f}/10")
        
        # Qualification
        qualification = results.get('qualification', {})
        table.add_row("Calificación", f"[bold yellow]{qualification.get('level', 'N/A')}[/bold yellow]")
        table.add_row("Probabilidad de Cierre", f"{qualification.get('close_probability', 0)}%")
        
        # ROI Potential
        roi_potential = results.get('roi_potential', {})
        table.add_row("ROI Potencial", f"{roi_potential.get('roi_percentage', 0):.0f}%")
        table.add_row("Período de Recuperación", f"{roi_potential.get('payback_months', 0):.1f} meses")
        
        self.console.print(table)
        
        # Pain points
        self.console.print("\n[yellow]Principales Pain Points:[/yellow]")
        for pain in results.get('pain_points', [])[:3]:
            self.console.print(f"• {pain['issue']} ({pain['severity']})")
    
    def _display_roi_results(self):
        """Display ROI calculation results"""
        roi = self.session_data.get('roi_analysis', {})
        
        if not roi:
            self.console.print("[red]No hay análisis ROI disponible[/red]")
            return
        
        summary = roi.get('executive_summary', {})
        
        # Create ROI table
        table = Table(title="Análisis de ROI", show_header=True)
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("ROI Año 1", f"[bold green]{summary.get('headline_roi', 0):.0f}%[/bold green]")
        table.add_row("Período de Recuperación", f"{summary.get('payback_period_months', 0):.1f} meses")
        table.add_row("Ahorro Anual", f"${summary.get('annual_savings_clp', 0)/1000000:.1f}M CLP")
        table.add_row("Nivel de Confianza", f"{summary.get('confidence_level', 0):.0f}%")
        
        self.console.print(table)
        
        # Scenarios
        self.console.print("\n[yellow]Escenarios de ROI:[/yellow]")
        expected_range = summary.get('expected_roi_range', {})
        self.console.print(f"• Conservador: {expected_range.get('conservative', 0):.0f}%")
        self.console.print(f"• Esperado: {expected_range.get('expected', 0):.0f}%")
        self.console.print(f"• Optimista: {expected_range.get('optimistic', 0):.0f}%")
    
    def _display_proposal_summary(self):
        """Display proposal summary"""
        proposal = self.session_data.get('proposal_data', {})
        
        if not proposal:
            self.console.print("[red]No hay propuesta disponible[/red]")
            return
        
        # Display metadata
        metadata = proposal.get('metadata', {})
        self.console.print(f"\n[cyan]Propuesta ID:[/cyan] {metadata.get('proposal_id', 'N/A')}")
        self.console.print(f"[cyan]Válida hasta:[/cyan] {metadata.get('valid_until', 'N/A')}")
        
        # Package info
        package = proposal.get('package', {})
        self.console.print(f"\n[yellow]Paquete:[/yellow] {package.get('name', 'N/A')}")
        self.console.print(f"[yellow]Duración:[/yellow] {package.get('duration', 'N/A')}")
        self.console.print(f"[yellow]Inversión:[/yellow] ${package.get('price_clp', 0)/1000000:.1f}M CLP")
    
    def _display_workflow_summary(self):
        """Display complete workflow summary"""
        self.console.print("\n[bold green]━━━ RESUMEN DEL FLUJO DE VENTA ━━━[/bold green]\n")
        
        # Client info
        client = self.session_data.get('client_data', {})
        self.console.print(f"[cyan]Cliente:[/cyan] {client.get('company_name', 'N/A')}")
        
        # Assessment summary
        assessment = self.session_data.get('assessment_results', {})
        qualification = assessment.get('qualification', {})
        self.console.print(f"[cyan]Calificación:[/cyan] {qualification.get('level', 'N/A')}")
        
        # ROI summary
        roi = self.session_data.get('roi_analysis', {})
        summary = roi.get('executive_summary', {})
        self.console.print(f"[cyan]ROI Proyectado:[/cyan] {summary.get('headline_roi', 0):.0f}%")
        
        # Proposal summary
        proposal = self.session_data.get('proposal_data', {})
        package = proposal.get('package', {})
        self.console.print(f"[cyan]Paquete Propuesto:[/cyan] {package.get('name', 'N/A')}")
        self.console.print(f"[cyan]Inversión:[/cyan] ${package.get('price_clp', 0)/1000000:.1f}M CLP")
        
        # Next action
        self.console.print(f"\n[bold yellow]Próximo Paso:[/bold yellow] {qualification.get('recommended_action', 'Agendar reunión')}")
    
    def _view_results(self):
        """View all current results"""
        self.console.print("\n[cyan]RESULTADOS ACTUALES DE LA SESIÓN[/cyan]\n")
        
        if self.session_data.get('client_data'):
            self.console.print("[green]✓[/green] Información del cliente")
        else:
            self.console.print("[red]✗[/red] Información del cliente")
        
        if self.session_data.get('assessment_results'):
            self.console.print("[green]✓[/green] Evaluación rápida completada")
            self._display_assessment_results()
        else:
            self.console.print("[red]✗[/red] Evaluación rápida")
        
        if self.session_data.get('roi_analysis'):
            self.console.print("[green]✓[/green] Análisis ROI completado")
            self._display_roi_results()
        else:
            self.console.print("[red]✗[/red] Análisis ROI")
        
        if self.session_data.get('proposal_data'):
            self.console.print("[green]✓[/green] Propuesta generada")
            self._display_proposal_summary()
        else:
            self.console.print("[red]✗[/red] Propuesta")
    
    def _export_all(self):
        """Export all documents"""
        self.console.print("\n[cyan]EXPORTANDO DOCUMENTOS[/cyan]")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Export assessment report
            if self.session_data.get('assessment_results'):
                task = progress.add_task("Exportando evaluación...", total=1)
                report = self.assessment_tool.generate_assessment_report()
                with open(f"{self.output_dir}/assessment_report.txt", 'w', encoding='utf-8') as f:
                    f.write(report)
                progress.update(task, completed=1)
            
            # Export ROI analysis
            if self.session_data.get('roi_analysis'):
                task = progress.add_task("Exportando análisis ROI...", total=2)
                
                # JSON
                with open(f"{self.output_dir}/roi_analysis.json", 'w', encoding='utf-8') as f:
                    json.dump(self.session_data['roi_analysis'], f, ensure_ascii=False, indent=2, default=str)
                progress.update(task, advance=1)
                
                # Excel
                self.roi_calculator.export_to_excel(f"{self.output_dir}/roi_analysis.xlsx")
                progress.update(task, advance=1)
            
            # Export proposal
            if self.session_data.get('proposal_data'):
                task = progress.add_task("Exportando propuesta...", total=3)
                
                # PDF
                self.proposal_generator.export_to_pdf(f"{self.output_dir}/proposal.pdf")
                progress.update(task, advance=1)
                
                # PowerPoint
                self.proposal_generator.export_to_powerpoint(f"{self.output_dir}/proposal.pptx")
                progress.update(task, advance=1)
                
                # One-pager
                one_pager = self.proposal_generator.generate_one_pager()
                with open(f"{self.output_dir}/executive_summary.txt", 'w', encoding='utf-8') as f:
                    f.write(one_pager)
                progress.update(task, advance=1)
            
            # Save session data
            task = progress.add_task("Guardando sesión...", total=1)
            with open(f"{self.output_dir}/session_data.json", 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, ensure_ascii=False, indent=2, default=str)
            progress.update(task, completed=1)
        
        self.console.print(f"\n[green]✓ Documentos exportados en:[/green] {self.output_dir}")
        
        # List exported files
        self.console.print("\n[yellow]Archivos generados:[/yellow]")
        for file in os.listdir(self.output_dir):
            self.console.print(f"  • {file}")
    
    def _load_session(self):
        """Load previous session data"""
        self.console.print("\n[cyan]CARGAR SESIÓN ANTERIOR[/cyan]")
        
        # List available sessions
        if os.path.exists('output'):
            sessions = [d for d in os.listdir('output') if d.startswith('session_')]
            
            if sessions:
                self.console.print("\n[yellow]Sesiones disponibles:[/yellow]")
                for i, session in enumerate(sessions, 1):
                    self.console.print(f"{i}. {session}")
                
                choice = IntPrompt.ask("Seleccione sesión", min_value=1, max_value=len(sessions))
                selected_session = sessions[choice - 1]
                
                # Load session data
                session_file = f"output/{selected_session}/session_data.json"
                if os.path.exists(session_file):
                    with open(session_file, 'r', encoding='utf-8') as f:
                        self.session_data = json.load(f)
                    
                    self.console.print(f"[green]✓ Sesión {selected_session} cargada exitosamente[/green]")
                    self._view_results()
                else:
                    self.console.print("[red]Error: Archivo de sesión no encontrado[/red]")
            else:
                self.console.print("[yellow]No hay sesiones guardadas[/yellow]")
        else:
            self.console.print("[yellow]No hay sesiones guardadas[/yellow]")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sales Toolkit - Herramientas Integradas de Venta para Consultoría E-commerce"
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Ejecutar flujo rápido de venta'
    )
    
    parser.add_argument(
        '--load',
        type=str,
        help='Cargar sesión específica'
    )
    
    args = parser.parse_args()
    
    # Create and run launcher
    launcher = SalesToolkitLauncher()
    
    if args.load:
        # Load specific session
        launcher.session_data = json.load(open(args.load, 'r', encoding='utf-8'))
        launcher._view_results()
    elif args.quick:
        # Run quick workflow
        launcher._quick_sales_workflow()
    else:
        # Interactive mode
        launcher.run()


if __name__ == "__main__":
    main()