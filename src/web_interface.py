"""
Flask Web Interface for ROI Calculator
Provides professional web-based ROI calculation with PDF generation
"""

import os
import json
import secrets
import logging
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import traceback
from dotenv import load_dotenv

from roi_calculator import ROICalculator
from pdf_generator import ROIPDFGenerator
from currency_converter import CurrencyConverter
from tax_calculator import TaxCalculator
from breakeven_analyzer import BreakEvenAnalyzer
from proposal_generator import ProposalGenerator
from cost_optimizer import CostOptimizer
from template_manager import TemplateManager
from batch_processor import BatchProcessor
from version_control import VersionControl

# Import database modules
from database.connection import get_session, init_database
from database.models import Calculation, Template, ComparisonScenario

# Import PowerPoint generator
from powerpoint_generator import PowerPointGenerator

# Load environment variables
load_dotenv()

# Initialize database
init_database()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create reports directory if it doesn't exist
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Initialize business tools
currency_converter = CurrencyConverter()
tax_calculator = TaxCalculator()
breakeven_analyzer = BreakEvenAnalyzer()
cost_optimizer = CostOptimizer(industry='ecommerce')
template_manager = TemplateManager()
batch_processor = BatchProcessor()
version_control = VersionControl()


@app.route('/')
def index():
    """Main calculator page"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200


@app.route('/calculate', methods=['POST'])
def calculate_roi():
    """Handle ROI calculation request"""
    try:
        # Get form data
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'annual_revenue', 'monthly_orders', 'avg_order_value',
            'labor_costs', 'shipping_costs', 'error_costs',
            'inventory_costs', 'service_investment'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing field in request: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        # Validate numeric values
        for field in required_fields:
            try:
                float(data[field])
            except (ValueError, TypeError):
                logger.warning(f"Invalid numeric value for field: {field}")
                return jsonify({'error': f'Invalid numeric value for field: {field}'}), 400
        
        # Convert strings to floats
        for field in required_fields:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                return jsonify({'error': f'Invalid value for {field}: must be a number'}), 400
        
        # Add optional fields
        data['company_name'] = data.get('company_name', 'Confidential Client')
        
        # Calculate ROI
        calculator = ROICalculator()
        results = calculator.calculate_roi(data)
        
        # Format results for JSON response
        formatted_results = format_results_for_json(results)
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'summary': calculator.get_summary_text()
        })
        
    except Exception as e:
        print(f"Error in calculation: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Calculation error: {str(e)}'}), 500


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF report"""
    try:
        data = request.get_json()
        
        if 'results' not in data:
            return jsonify({'error': 'No calculation results provided'}), 400
        
        results = data['results']
        
        # Generate PDF
        pdf_generator = ROIPDFGenerator(results)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_name = results.get('inputs', {}).get('company_name', 'client')
        safe_company_name = secure_filename(company_name.replace(' ', '_'))
        filename = f"roi_report_{safe_company_name}_{timestamp}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Generate PDF
        pdf_generator.generate_pdf(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': url_for('download_report', filename=filename)
        })
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'PDF generation error: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_report(filename):
    """Download generated PDF report"""
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(REPORTS_DIR, safe_filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=safe_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Error downloading file: {e}")
        return jsonify({'error': 'Download error'}), 500


@app.route('/api/examples')
def get_examples():
    """Get example scenarios"""
    examples = {
        'small_business': {
            'name': 'Small E-commerce Business',
            'description': 'Startup or small business with basic operations',
            'data': {
                'company_name': 'Small E-commerce Co.',
                'annual_revenue': 500000,
                'monthly_orders': 1500,
                'avg_order_value': 27.78,
                'labor_costs': 3000,
                'shipping_costs': 2000,
                'error_costs': 500,
                'inventory_costs': 1000,
                'service_investment': 25000
            }
        },
        'medium_business': {
            'name': 'Medium E-commerce Business',
            'description': 'Established business with growing operations',
            'data': {
                'company_name': 'Growing E-commerce Ltd.',
                'annual_revenue': 2000000,
                'monthly_orders': 5000,
                'avg_order_value': 33.33,
                'labor_costs': 8000,
                'shipping_costs': 5000,
                'error_costs': 2000,
                'inventory_costs': 3000,
                'service_investment': 50000
            }
        },
        'large_business': {
            'name': 'Large E-commerce Business',
            'description': 'Established enterprise with complex operations',
            'data': {
                'company_name': 'Enterprise E-commerce Corp.',
                'annual_revenue': 5000000,
                'monthly_orders': 12000,
                'avg_order_value': 34.72,
                'labor_costs': 20000,
                'shipping_costs': 12000,
                'error_costs': 5000,
                'inventory_costs': 8000,
                'service_investment': 100000
            }
        }
    }
    
    return jsonify(examples)


@app.route('/api/save-calculation', methods=['POST'])
def save_calculation():
    """Save a calculation to the database"""
    try:
        data = request.json
        session = get_session()
        
        # Create new calculation record
        calc = Calculation(
            company_name=data.get('company_name'),
            annual_revenue=data['annual_revenue'],
            monthly_orders=data['monthly_orders'],
            avg_order_value=data['avg_order_value'],
            labor_costs=data['labor_costs'],
            shipping_costs=data['shipping_costs'],
            error_costs=data['error_costs'],
            inventory_costs=data['inventory_costs'],
            service_investment=data['service_investment'],
            results=data.get('results', {}),
            notes=data.get('notes'),
            tags=data.get('tags')
        )
        
        session.add(calc)
        session.commit()
        
        result = {
            'success': True,
            'message': 'Calculation saved successfully',
            'id': calc.id
        }
        
        session.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error saving calculation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error saving calculation: {str(e)}'
        }), 500


@app.route('/api/calculations')
def get_calculations():
    """Get all saved calculations"""
    try:
        session = get_session()
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        search = request.args.get('search', '')
        
        # Build query
        query = session.query(Calculation)
        
        if search:
            query = query.filter(
                Calculation.company_name.ilike(f'%{search}%')
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        calculations = query.order_by(Calculation.created_at.desc())\
                           .limit(limit)\
                           .offset(offset)\
                           .all()
        
        result = {
            'success': True,
            'total': total,
            'calculations': [calc.to_dict() for calc in calculations]
        }
        
        session.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching calculations: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching calculations: {str(e)}'
        }), 500


@app.route('/api/calculation/<int:calc_id>')
def get_calculation(calc_id):
    """Get a specific calculation by ID"""
    try:
        session = get_session()
        calc = session.query(Calculation).get(calc_id)
        
        if not calc:
            return jsonify({
                'success': False,
                'message': 'Calculation not found'
            }), 404
        
        result = {
            'success': True,
            'calculation': calc.to_dict()
        }
        
        session.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching calculation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching calculation: {str(e)}'
        }), 500


@app.route('/api/calculation/<int:calc_id>', methods=['DELETE'])
def delete_calculation(calc_id):
    """Delete a calculation"""
    try:
        session = get_session()
        calc = session.query(Calculation).get(calc_id)
        
        if not calc:
            return jsonify({
                'success': False,
                'message': 'Calculation not found'
            }), 404
        
        session.delete(calc)
        session.commit()
        
        result = {
            'success': True,
            'message': 'Calculation deleted successfully'
        }
        
        session.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error deleting calculation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error deleting calculation: {str(e)}'
        }), 500


@app.route('/history')
def history():
    """Calculation history page"""
    return render_template('history.html')


@app.route('/compare')
def compare():
    """Comparison view page"""
    return render_template('compare.html')


@app.route('/whatif')
def whatif():
    """What-If Analysis page"""
    return render_template('whatif.html')


@app.route('/sensitivity')
def sensitivity():
    """Sensitivity Analysis page"""
    return render_template('sensitivity.html')


@app.route('/api/whatif-calculate', methods=['POST'])
def whatif_calculate():
    """Calculate ROI with adjusted parameters for what-if analysis"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'annual_revenue', 'monthly_orders', 'avg_order_value',
            'labor_costs', 'shipping_costs', 'error_costs',
            'inventory_costs', 'service_investment'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert strings to floats
        for field in required_fields:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                return jsonify({'error': f'Invalid value for {field}: must be a number'}), 400
        
        # Add optional fields
        data['company_name'] = data.get('company_name', 'What-If Analysis')
        
        # Calculate ROI with adjusted values
        calculator = ROICalculator()
        results = calculator.calculate_roi(data)
        
        # Format results for JSON response
        formatted_results = format_results_for_json(results)
        
        return jsonify({
            'success': True,
            'results': formatted_results
        })
        
    except Exception as e:
        print(f"Error in what-if calculation: {e}")
        return jsonify({'error': f'Calculation error: {str(e)}'}), 500


@app.route('/api/sensitivity-calculate', methods=['POST'])
def sensitivity_calculate():
    """Calculate sensitivity analysis for ROI variables"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'annual_revenue', 'monthly_orders', 'avg_order_value',
            'labor_costs', 'shipping_costs', 'error_costs',
            'inventory_costs', 'service_investment'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert strings to floats
        for field in required_fields:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                return jsonify({'error': f'Invalid value for {field}: must be a number'}), 400
        
        # Add optional fields
        data['company_name'] = data.get('company_name', 'Sensitivity Analysis')
        
        # Calculate base case ROI
        calculator = ROICalculator()
        base_results = calculator.calculate_roi(data)
        base_roi = base_results['roi_metrics']['first_year_roi']
        
        # Define sensitivity test ranges
        test_ranges = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]  # -30% to +30%
        
        # Variables to test (excluding service_investment as it's the investment, not a variable cost/revenue)
        variables_to_test = {
            'annual_revenue': 'Annual Revenue',
            'monthly_orders': 'Monthly Orders', 
            'avg_order_value': 'Average Order Value',
            'labor_costs': 'Labor Costs',
            'shipping_costs': 'Shipping Costs',
            'error_costs': 'Error Costs',
            'inventory_costs': 'Inventory Costs'
        }
        
        sensitivity_results = {}
        
        # Calculate sensitivity for each variable
        for var_name, var_label in variables_to_test.items():
            original_value = data[var_name]
            roi_values = []
            
            for multiplier in test_ranges:
                test_data = data.copy()
                test_data[var_name] = original_value * multiplier
                
                try:
                    test_results = calculator.calculate_roi(test_data)
                    test_roi = test_results['roi_metrics']['first_year_roi']
                    roi_values.append({
                        'change_percent': (multiplier - 1.0) * 100,
                        'roi': test_roi,
                        'roi_change': test_roi - base_roi,
                        'roi_change_percent': ((test_roi - base_roi) / base_roi * 100) if base_roi != 0 else 0
                    })
                except:
                    roi_values.append({
                        'change_percent': (multiplier - 1.0) * 100,
                        'roi': 0,
                        'roi_change': -base_roi,
                        'roi_change_percent': -100
                    })
            
            # Calculate sensitivity coefficient (elasticity)
            # Using the 10% changes (±10%) for coefficient calculation
            try:
                roi_at_plus_10 = next(r['roi'] for r in roi_values if abs(r['change_percent'] - 10.0) < 0.1)
                roi_at_minus_10 = next(r['roi'] for r in roi_values if abs(r['change_percent'] - (-10.0)) < 0.1)
                
                sensitivity_coefficient = ((roi_at_plus_10 - roi_at_minus_10) / base_roi) / 0.2 if base_roi != 0 else 0
                
                # Calculate break-even point (where ROI = 0)
                break_even_multiplier = None
                for i, result in enumerate(roi_values):
                    if result['roi'] <= 0:
                        if i > 0:
                            # Linear interpolation to find exact break-even
                            prev_result = roi_values[i-1]
                            if prev_result['roi'] > 0:
                                # Interpolate between prev_result and current result
                                roi_diff = prev_result['roi'] - result['roi']
                                change_diff = result['change_percent'] - prev_result['change_percent']
                                break_even_change = prev_result['change_percent'] + (prev_result['roi'] / roi_diff) * change_diff
                                break_even_multiplier = 1 + (break_even_change / 100)
                                break
                        else:
                            break_even_multiplier = 1 + (result['change_percent'] / 100)
                        break
                
            except:
                sensitivity_coefficient = 0
                break_even_multiplier = None
            
            sensitivity_results[var_name] = {
                'label': var_label,
                'coefficient': sensitivity_coefficient,
                'roi_values': roi_values,
                'break_even_multiplier': break_even_multiplier,
                'break_even_percent': ((break_even_multiplier - 1.0) * 100) if break_even_multiplier else None
            }
        
        # Calculate variable rankings by absolute sensitivity coefficient
        rankings = sorted(sensitivity_results.items(), 
                         key=lambda x: abs(x[1]['coefficient']), 
                         reverse=True)
        
        # Monte Carlo simulation (simplified)
        monte_carlo_results = run_monte_carlo_simulation(data, calculator, 1000)
        
        return jsonify({
            'success': True,
            'base_roi': base_roi,
            'base_data': data,
            'sensitivity_results': sensitivity_results,
            'rankings': [(var, result['label'], result['coefficient']) for var, result in rankings],
            'monte_carlo': monte_carlo_results
        })
        
    except Exception as e:
        print(f"Error in sensitivity analysis: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': f'Sensitivity analysis error: {str(e)}'}), 500


def run_monte_carlo_simulation(base_data, calculator, num_simulations=1000):
    """Run Monte Carlo simulation for risk analysis"""
    import random
    
    roi_results = []
    
    # Define volatility for each variable (standard deviation as % of mean)
    volatilities = {
        'annual_revenue': 0.15,      # 15% volatility
        'monthly_orders': 0.12,      # 12% volatility  
        'avg_order_value': 0.10,     # 10% volatility
        'labor_costs': 0.08,         # 8% volatility
        'shipping_costs': 0.20,      # 20% volatility (more volatile)
        'error_costs': 0.25,         # 25% volatility (most volatile)
        'inventory_costs': 0.15      # 15% volatility
    }
    
    for _ in range(num_simulations):
        sim_data = base_data.copy()
        
        # Apply random variations to each variable
        for var_name, volatility in volatilities.items():
            if var_name in sim_data:
                original_value = base_data[var_name]
                # Use normal distribution with specified volatility
                random_factor = random.gauss(1.0, volatility)
                # Ensure positive values
                random_factor = max(0.1, random_factor)
                sim_data[var_name] = original_value * random_factor
        
        try:
            results = calculator.calculate_roi(sim_data)
            roi = results['roi_metrics']['first_year_roi']
            roi_results.append(roi)
        except:
            roi_results.append(0)  # Failed calculation
    
    # Calculate statistics
    roi_results.sort()
    mean_roi = sum(roi_results) / len(roi_results)
    
    # Percentiles
    p10 = roi_results[int(0.10 * len(roi_results))]
    p25 = roi_results[int(0.25 * len(roi_results))]
    p50 = roi_results[int(0.50 * len(roi_results))]
    p75 = roi_results[int(0.75 * len(roi_results))]
    p90 = roi_results[int(0.90 * len(roi_results))]
    
    # Risk metrics
    probability_positive = len([r for r in roi_results if r > 0]) / len(roi_results)
    probability_target = len([r for r in roi_results if r > 0.15]) / len(roi_results)  # 15% ROI target
    
    return {
        'mean_roi': mean_roi,
        'percentiles': {
            'p10': p10,
            'p25': p25, 
            'p50': p50,
            'p75': p75,
            'p90': p90
        },
        'risk_metrics': {
            'probability_positive': probability_positive,
            'probability_15_percent': probability_target,
            'value_at_risk_90': p10,  # 90% confidence interval
            'upside_potential': p90
        },
        'distribution': roi_results[::50]  # Sample every 50th result for visualization
    }


@app.route('/api/whatif-scenarios')
def get_whatif_scenarios():
    """Get predefined what-if scenarios"""
    scenarios = {
        'best_case': {
            'name': 'Best Case Scenario',
            'description': 'Optimistic projections with higher revenue and lower costs',
            'adjustments': {
                'annual_revenue': 1.25,  # +25%
                'monthly_orders': 1.20,  # +20%
                'avg_order_value': 1.15,  # +15%
                'labor_costs': 0.85,     # -15%
                'shipping_costs': 0.80,  # -20%
                'error_costs': 0.70,     # -30%
                'inventory_costs': 0.75, # -25%
                'service_investment': 1.0 # No change
            }
        },
        'worst_case': {
            'name': 'Worst Case Scenario',
            'description': 'Conservative projections with lower revenue and higher costs',
            'adjustments': {
                'annual_revenue': 0.80,  # -20%
                'monthly_orders': 0.85,  # -15%
                'avg_order_value': 0.90, # -10%
                'labor_costs': 1.15,     # +15%
                'shipping_costs': 1.20,  # +20%
                'error_costs': 1.25,     # +25%
                'inventory_costs': 1.10, # +10%
                'service_investment': 1.0 # No change
            }
        },
        'most_likely': {
            'name': 'Most Likely Scenario',
            'description': 'Realistic projections based on market conditions',
            'adjustments': {
                'annual_revenue': 1.05,  # +5%
                'monthly_orders': 1.03,  # +3%
                'avg_order_value': 1.02, # +2%
                'labor_costs': 0.95,     # -5%
                'shipping_costs': 0.92,  # -8%
                'error_costs': 0.85,     # -15%
                'inventory_costs': 0.90, # -10%
                'service_investment': 1.0 # No change
            }
        }
    }
    
    return jsonify(scenarios)


@app.route('/api/whatif-save', methods=['POST'])
def save_whatif_scenario():
    """Save a what-if scenario"""
    try:
        data = request.json
        session = get_session()
        
        # Create new calculation record with what-if tag
        calc = Calculation(
            company_name=data.get('company_name', 'What-If Analysis'),
            annual_revenue=data['annual_revenue'],
            monthly_orders=data['monthly_orders'],
            avg_order_value=data['avg_order_value'],
            labor_costs=data['labor_costs'],
            shipping_costs=data['shipping_costs'],
            error_costs=data['error_costs'],
            inventory_costs=data['inventory_costs'],
            service_investment=data['service_investment'],
            results=data.get('results', {}),
            notes=data.get('notes', ''),
            tags=f"what-if,{data.get('tags', '')}"
        )
        
        session.add(calc)
        session.commit()
        
        result = {
            'success': True,
            'message': 'What-if scenario saved successfully',
            'id': calc.id
        }
        
        session.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error saving what-if scenario: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error saving scenario: {str(e)}'
        }), 500


@app.route('/api/compare', methods=['POST'])
def compare_calculations():
    """Compare multiple calculations"""
    try:
        data = request.json
        calculation_ids = data.get('calculation_ids', [])
        
        if len(calculation_ids) < 2 or len(calculation_ids) > 3:
            return jsonify({
                'success': False,
                'message': 'Please select 2-3 calculations to compare'
            }), 400
        
        session = get_session()
        calculations = []
        
        for calc_id in calculation_ids:
            calc = session.query(Calculation).get(calc_id)
            if calc:
                calculations.append(calc.to_dict())
        
        session.close()
        
        if len(calculations) != len(calculation_ids):
            return jsonify({
                'success': False,
                'message': 'Some calculations were not found'
            }), 404
        
        # Process calculations for comparison
        comparison_data = process_comparison_data(calculations)
        
        return jsonify({
            'success': True,
            'calculations': calculations,
            'comparison': comparison_data
        })
        
    except Exception as e:
        logger.error(f"Error comparing calculations: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error comparing calculations: {str(e)}'
        }), 500


@app.route('/api/templates')
def get_templates():
    """Get all templates from database"""
    try:
        session = get_session()
        templates = session.query(Template).all()
        
        result = {
            'success': True,
            'templates': [template.to_dict() for template in templates]
        }
        
        session.close()
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching templates: {str(e)}'
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_inputs():
    """Validate input data"""
    try:
        data = request.get_json()
        errors = []
        
        # Required fields validation
        required_fields = {
            'annual_revenue': 'Annual Revenue',
            'monthly_orders': 'Monthly Orders',
            'avg_order_value': 'Average Order Value',
            'labor_costs': 'Labor Costs',
            'shipping_costs': 'Shipping Costs',
            'error_costs': 'Error Costs',
            'inventory_costs': 'Inventory Costs',
            'service_investment': 'Service Investment'
        }
        
        for field, label in required_fields.items():
            if field not in data or data[field] is None or data[field] == '':
                errors.append(f'{label} is required')
                continue
                
            try:
                value = float(data[field])
                if value < 0:
                    errors.append(f'{label} must be a positive number')
                elif field == 'annual_revenue' and value < 10000:
                    errors.append(f'{label} seems too low (minimum $10,000)')
                elif field == 'service_investment' and value < 1000:
                    errors.append(f'{label} seems too low (minimum $1,000)')
            except (ValueError, TypeError):
                errors.append(f'{label} must be a valid number')
        
        # Business logic validation
        if not errors:
            try:
                revenue = float(data['annual_revenue'])
                orders = float(data['monthly_orders'])
                aov = float(data['avg_order_value'])
                
                # Check if monthly revenue matches orders * AOV
                expected_monthly_revenue = orders * aov
                actual_monthly_revenue = revenue / 12
                
                if abs(expected_monthly_revenue - actual_monthly_revenue) / actual_monthly_revenue > 0.1:
                    errors.append('Monthly orders × Average order value should approximately equal monthly revenue')
                
                # Check if costs are reasonable relative to revenue
                total_monthly_costs = sum([
                    float(data['labor_costs']),
                    float(data['shipping_costs']),
                    float(data['error_costs']),
                    float(data['inventory_costs'])
                ])
                
                if total_monthly_costs > actual_monthly_revenue:
                    errors.append('Total monthly costs exceed monthly revenue - please verify your inputs')
                
            except (ValueError, KeyError):
                pass  # Individual field errors already caught above
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 500


def format_results_for_json(results):
    """Format calculation results for JSON serialization"""
    # Deep copy to avoid modifying original
    formatted = {}
    
    def convert_item(item):
        if isinstance(item, dict):
            return {k: convert_item(v) for k, v in item.items()}
        elif isinstance(item, (list, tuple)):
            return [convert_item(i) for i in item]
        elif isinstance(item, (int, float)):
            return round(float(item), 2)
        else:
            return item
    
    return convert_item(results)


def process_comparison_data(calculations):
    """Process calculations for comparison analysis"""
    comparison = {
        'metrics': [],
        'differences': {},
        'rankings': {}
    }
    
    # Extract key metrics from each calculation
    metrics = []
    for calc in calculations:
        roi_metrics = calc.get('results', {}).get('roi_metrics', {})
        financial = calc.get('results', {}).get('financial_metrics', {})
        projections = calc.get('results', {}).get('projections', {})
        
        metric = {
            'id': calc['id'],
            'company_name': calc['company_name'],
            'annual_revenue': calc['annual_revenue'],
            'service_investment': calc['service_investment'],
            'roi': roi_metrics.get('first_year_roi', 0),
            'payback_months': roi_metrics.get('payback_period_months', 0),
            'annual_savings': roi_metrics.get('annual_savings', 0),
            'monthly_savings': roi_metrics.get('monthly_savings', 0),
            'npv': financial.get('npv', 0),
            'irr': financial.get('irr', 0) * 100,  # Convert to percentage
            'year_3_roi': projections.get('year_3', {}).get('roi_percentage', 0)
        }
        metrics.append(metric)
    
    comparison['metrics'] = metrics
    
    # Calculate differences and rankings
    if len(metrics) >= 2:
        # Find best and worst for each metric
        metrics_to_rank = ['roi', 'annual_savings', 'npv', 'irr', 'year_3_roi']
        metrics_to_rank_inverse = ['payback_months', 'service_investment']  # Lower is better
        
        for metric_key in metrics_to_rank:
            values = [(i, m[metric_key]) for i, m in enumerate(metrics)]
            values.sort(key=lambda x: x[1], reverse=True)
            comparison['rankings'][metric_key] = [idx for idx, _ in values]
        
        for metric_key in metrics_to_rank_inverse:
            values = [(i, m[metric_key]) for i, m in enumerate(metrics)]
            values.sort(key=lambda x: x[1])
            comparison['rankings'][metric_key] = [idx for idx, _ in values]
        
        # Calculate percentage differences from the best performer
        comparison['differences'] = calculate_percentage_differences(metrics)
    
    return comparison


def calculate_percentage_differences(metrics):
    """Calculate percentage differences between calculations"""
    differences = {}
    
    if len(metrics) < 2:
        return differences
    
    # For each metric, calculate difference from the best performer
    metric_keys = ['roi', 'annual_savings', 'npv', 'irr', 'year_3_roi']
    inverse_metrics = ['payback_months', 'service_investment']
    
    for key in metric_keys:
        values = [m[key] for m in metrics]
        best_value = max(values)
        if best_value > 0:
            differences[key] = [(v - best_value) / best_value * 100 for v in values]
        else:
            differences[key] = [0] * len(values)
    
    for key in inverse_metrics:
        values = [m[key] for m in metrics]
        best_value = min(v for v in values if v > 0)
        if best_value > 0:
            differences[key] = [(v - best_value) / best_value * 100 for v in values]
        else:
            differences[key] = [0] * len(values)
    
    return differences


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# Add some utility routes for the frontend
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/currency-info')
def currency_info():
    """Get currency and market information"""
    return jsonify({
        'base_currency': 'USD',
        'chilean_iva_rate': 0.19,
        'inflation_rate': 0.035,
        'last_updated': '2024-01-01'
    })


@app.route('/market-insights')
def market_insights():
    """Market Insights page with FRED data and benchmarking"""
    try:
        from market_data_service import MarketDataService
        
        fred_api_key = os.environ.get('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
        market_service = MarketDataService(fred_api_key)
        
        # Get market overview
        market_overview = market_service.get_market_overview()
        
        return render_template('market_insights.html', market_overview=market_overview)
    except Exception as e:
        logger.error(f"Error loading market insights: {str(e)}")
        # Return page with error state
        return render_template('market_insights.html', error=str(e))


@app.route('/api/market-data/update', methods=['POST'])
def update_market_data():
    """Update market data from FRED API"""
    try:
        from market_data_service import MarketDataService
        
        fred_api_key = os.environ.get('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
        market_service = MarketDataService(fred_api_key)
        
        # Get series to update from request - handle empty JSON body gracefully
        try:
            data = request.get_json() or {}
        except Exception as json_error:
            logger.warning(f"Could not parse JSON from request: {str(json_error)}")
            data = {}
        
        series_ids = data.get('series_ids', None) if data else None
        
        # Update data
        results = market_service.update_market_data(series_ids)
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Updated {len([r for r in results.values() if r])} series successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating market data: {str(e)}")
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@app.route('/api/market-data/<series_id>')
def get_market_data(series_id):
    """Get market data for a specific series"""
    try:
        from market_data_service import MarketDataService
        
        fred_api_key = os.environ.get('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
        market_service = MarketDataService(fred_api_key)
        
        days = request.args.get('days', 365, type=int)
        data = market_service.get_latest_data(series_id, days)
        
        return jsonify({
            'success': True,
            'series_id': series_id,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"Error getting market data for {series_id}: {str(e)}")
        return jsonify({'error': f'Data retrieval failed: {str(e)}'}), 500


@app.route('/api/roi-benchmark', methods=['POST'])
def roi_benchmark():
    """Generate ROI benchmarks and percentile ranking"""
    try:
        from market_data_service import MarketDataService
        
        data = request.get_json()
        roi_value = float(data.get('roi_value', 0))
        industry = data.get('industry', 'ecommerce')
        
        fred_api_key = os.environ.get('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
        market_service = MarketDataService(fred_api_key)
        
        benchmarks = market_service.generate_roi_benchmarks(roi_value, industry)
        
        return jsonify({
            'success': True,
            'benchmarks': benchmarks
        })
        
    except Exception as e:
        logger.error(f"Error generating ROI benchmark: {str(e)}")
        return jsonify({'error': f'Benchmark generation failed: {str(e)}'}), 500


@app.route('/api/market-overview')
def market_overview():
    """Get comprehensive market overview"""
    try:
        from market_data_service import MarketDataService
        
        fred_api_key = os.environ.get('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
        market_service = MarketDataService(fred_api_key)
        
        overview = market_service.get_market_overview()
        
        return jsonify({
            'success': True,
            'overview': overview,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating market overview: {str(e)}")
        return jsonify({'error': f'Overview generation failed: {str(e)}'}), 500


@app.route('/api/trend-analysis/<series_id>')
def trend_analysis(series_id):
    """Get trend analysis for a market data series"""
    try:
        from market_data_service import MarketDataService
        
        fred_api_key = os.environ.get('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
        market_service = MarketDataService(fred_api_key)
        
        days = request.args.get('days', 365, type=int)
        analysis = market_service.get_trend_analysis(series_id, days)
        
        return jsonify({
            'success': True,
            'series_id': series_id,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error generating trend analysis for {series_id}: {str(e)}")
        return jsonify({'error': f'Trend analysis failed: {str(e)}'}), 500


@app.route('/api/fred-test')
def fred_api_test():
    """Test FRED API connection"""
    try:
        from market_data_service import test_fred_api_connection
        
        fred_api_key = os.environ.get('FRED_API_KEY', 'c5ed99d76664a2191ccfd433edd9af6d')
        result = test_fred_api_connection(fred_api_key)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error testing FRED API: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})


# =============================================================================
# BUSINESS TOOLS ROUTES - Currency, Tax, Break-Even Analysis
# =============================================================================

@app.route('/api/currencies')
def get_currencies():
    """Get supported currencies and current exchange rates"""
    try:
        currencies = currency_converter.get_supported_currencies()
        rates = currency_converter.get_current_rates()
        return jsonify({
            'currencies': currencies,
            'rates': rates
        })
    except Exception as e:
        logger.error(f"Error getting currencies: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/currency-convert', methods=['POST'])
def convert_currency():
    """Convert amount between currencies"""
    try:
        data = request.json
        amount = float(data['amount'])
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        
        result = currency_converter.convert(amount, from_currency, to_currency)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/update-exchange-rates', methods=['POST'])
def update_exchange_rates():
    """Update exchange rates from API"""
    try:
        success = currency_converter.update_rates()
        return jsonify({
            'success': success,
            'rates': currency_converter.get_current_rates()
        })
    except Exception as e:
        logger.error(f"Error updating exchange rates: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tax-jurisdictions')
def get_tax_jurisdictions():
    """Get available tax jurisdictions"""
    try:
        jurisdictions = tax_calculator.get_available_jurisdictions()
        return jsonify({'jurisdictions': jurisdictions})
    except Exception as e:
        logger.error(f"Error getting tax jurisdictions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tax-regions/<jurisdiction>')
def get_tax_regions(jurisdiction):
    """Get regions for a specific jurisdiction"""
    try:
        regions = tax_calculator.get_regions_for_jurisdiction(jurisdiction)
        jurisdiction_info = tax_calculator.get_jurisdiction_info(jurisdiction)
        return jsonify({
            'regions': regions,
            'jurisdiction_info': jurisdiction_info
        })
    except Exception as e:
        logger.error(f"Error getting tax regions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/calculate-with-currency-tax', methods=['POST'])
def calculate_with_currency_tax():
    """Calculate ROI with currency conversion and tax considerations"""
    try:
        data = request.json
        
        # Extract ROI inputs
        roi_inputs = {
            'annual_revenue': float(data['annual_revenue']),
            'monthly_orders': float(data['monthly_orders']),
            'avg_order_value': float(data['avg_order_value']),
            'labor_costs': float(data['labor_costs']),
            'shipping_costs': float(data['shipping_costs']),
            'error_costs': float(data['error_costs']),
            'inventory_costs': float(data['inventory_costs']),
            'service_investment': float(data['service_investment']),
            'company_name': data.get('company_name', 'Client')
        }
        
        # Calculate base ROI
        calculator = ROICalculator()
        results = calculator.calculate_roi(roi_inputs)
        
        # Apply currency conversion if requested
        target_currency = data.get('target_currency')
        if target_currency and target_currency != 'USD':
            results = currency_converter.convert_roi_calculation(results, target_currency)
        
        # Apply tax calculations if requested
        tax_config = data.get('tax_config')
        if tax_config and tax_config.get('jurisdiction'):
            # Validate tax configuration
            validation_errors = tax_calculator.validate_tax_config(tax_config)
            if validation_errors:
                return jsonify({'error': f"Tax configuration errors: {', '.join(validation_errors)}"}), 400
            
            results = tax_calculator.calculate_roi_tax_impact(results, tax_config)
        
        # Add metadata
        results['calculation_metadata'] = {
            'currency_converted': target_currency is not None and target_currency != 'USD',
            'target_currency': target_currency,
            'tax_applied': tax_config is not None and tax_config.get('jurisdiction') is not None,
            'tax_config': tax_config,
            'calculation_timestamp': datetime.now().isoformat()
        }
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in currency/tax calculation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/breakeven')
def breakeven_page():
    """Break-even analysis page"""
    return render_template('breakeven.html')


@app.route('/api/breakeven-analysis', methods=['POST'])
def perform_breakeven_analysis():
    """Perform comprehensive break-even analysis"""
    try:
        data = request.json
        
        # Extract ROI inputs
        roi_inputs = {
            'annual_revenue': float(data['annual_revenue']),
            'monthly_orders': float(data['monthly_orders']),
            'avg_order_value': float(data['avg_order_value']),
            'labor_costs': float(data['labor_costs']),
            'shipping_costs': float(data['shipping_costs']),
            'error_costs': float(data['error_costs']),
            'inventory_costs': float(data['inventory_costs']),
            'service_investment': float(data['service_investment'])
        }
        
        # Get variable ranges for sensitivity analysis
        variable_ranges = data.get('variable_ranges')
        
        # Perform break-even analysis
        analysis = breakeven_analyzer.analyze_breakeven_scenarios(roi_inputs, variable_ranges)
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error in break-even analysis: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/breakeven-summary', methods=['POST'])
def get_breakeven_summary():
    """Get break-even analysis summary"""
    try:
        data = request.json
        
        roi_inputs = {
            'annual_revenue': float(data['annual_revenue']),
            'monthly_orders': float(data['monthly_orders']),
            'avg_order_value': float(data['avg_order_value']),
            'labor_costs': float(data['labor_costs']),
            'shipping_costs': float(data['shipping_costs']),
            'error_costs': float(data['error_costs']),
            'inventory_costs': float(data['inventory_costs']),
            'service_investment': float(data['service_investment'])
        }
        
        # Perform quick break-even analysis
        analysis = breakeven_analyzer.analyze_breakeven_scenarios(roi_inputs)
        summary = breakeven_analyzer.get_summary()
        
        return jsonify({
            'summary_text': summary,
            'key_metrics': {
                'payback_months': analysis.get('time_to_breakeven', {}).get('basic_payback_months'),
                'risk_level': analysis.get('risk_assessment', {}).get('risk_level'),
                'breakeven_points': analysis.get('breakeven_points', {})
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting break-even summary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/currency-tax-config')
def currency_tax_config_page():
    """Currency and tax configuration page"""
    return render_template('currency_tax_config.html')


# =============================================================================
# PROPOSAL GENERATOR ROUTES
# =============================================================================

@app.route('/proposal')
def proposal_page():
    """Proposal generator page"""
    return render_template('proposal_generator.html')


@app.route('/powerpoint')
def powerpoint_page():
    """PowerPoint generator page"""
    return render_template('powerpoint_export.html')


@app.route('/api/generate-proposal', methods=['POST'])
def generate_proposal():
    """Generate professional sales proposal"""
    try:
        data = request.get_json()
        
        # Validate required data
        if 'results' not in data:
            return jsonify({'error': 'ROI calculation results required'}), 400
        
        results = data['results']
        format_type = data.get('format', 'all')  # pdf, docx, html, or all
        template_name = data.get('template', 'professional')
        
        # Company branding configuration
        company_config = data.get('company_config', {})
        
        # Generate proposal
        generator = ProposalGenerator(results, company_config)
        proposal_files = generator.generate_proposal(format_type, template_name)
        
        # Move files to reports directory for download
        download_urls = {}
        for file_format, filepath in proposal_files.items():
            if filepath and os.path.exists(filepath):
                filename = os.path.basename(filepath)
                # Copy to reports directory
                reports_filepath = os.path.join(REPORTS_DIR, filename)
                import shutil
                shutil.copy2(filepath, reports_filepath)
                download_urls[file_format] = url_for('download_report', filename=filename)
        
        return jsonify({
            'success': True,
            'proposal_files': download_urls,
            'message': f'Generated {len(download_urls)} proposal file(s)'
        })
        
    except Exception as e:
        logger.error(f"Error generating proposal: {str(e)}")
        return jsonify({'error': f'Proposal generation failed: {str(e)}'}), 500


@app.route('/api/proposal-templates')
def get_proposal_templates():
    """Get available proposal templates"""
    templates = {
        'professional': {
            'name': 'Professional',
            'description': 'Clean, corporate design suitable for enterprise clients',
            'preview_url': '/static/images/template_professional.png'
        },
        'modern': {
            'name': 'Modern',
            'description': 'Contemporary design with bold colors and graphics',
            'preview_url': '/static/images/template_modern.png'
        },
        'executive': {
            'name': 'Executive',
            'description': 'Elegant, minimal design for C-level presentations',
            'preview_url': '/static/images/template_executive.png'
        }
    }
    
    return jsonify({
        'success': True,
        'templates': templates
    })


@app.route('/api/company-branding')
def get_company_branding():
    """Get company branding options"""
    branding_options = {
        'colors': {
            'professional': {'primary': '#2E5BBA', 'secondary': '#8FA4D3', 'accent': '#D4AF37'},
            'modern': {'primary': '#FF6B6B', 'secondary': '#4ECDC4', 'accent': '#FFE66D'},
            'corporate': {'primary': '#1B365D', 'secondary': '#5D737E', 'accent': '#B8860B'},
            'tech': {'primary': '#6C5CE7', 'secondary': '#A29BFE', 'accent': '#00B894'},
            'finance': {'primary': '#2D3436', 'secondary': '#636E72', 'accent': '#00B894'}
        },
        'fonts': ['Segoe UI', 'Arial', 'Helvetica', 'Times New Roman', 'Calibri'],
        'logo_guidelines': {
            'max_size': '2MB',
            'formats': ['PNG', 'JPG', 'SVG'],
            'recommended_dimensions': '300x100 pixels'
        }
    }
    
    return jsonify({
        'success': True,
        'branding_options': branding_options
    })


# =============================================================================
# POWERPOINT GENERATOR ROUTES
# =============================================================================

@app.route('/api/generate-powerpoint', methods=['POST'])
def generate_powerpoint():
    """Generate PowerPoint presentation"""
    try:
        data = request.get_json()
        
        # Validate required data
        if 'results' not in data:
            return jsonify({'error': 'ROI calculation results required'}), 400
        
        results = data['results']
        template_name = data.get('template', 'executive')  # executive, sales, technical
        
        # Company branding configuration
        company_config = data.get('company_config', {})
        
        # Custom color scheme
        color_scheme = data.get('color_scheme', {})
        
        # Speaker notes configuration
        include_speaker_notes = data.get('include_speaker_notes', True)
        
        # Generate PowerPoint
        generator = PowerPointGenerator(results, company_config)
        
        # Apply custom configuration
        custom_config = {}
        if color_scheme:
            custom_config.update(color_scheme)
        if not include_speaker_notes:
            custom_config['include_speaker_notes'] = False
            
        presentation_file = generator.generate_presentation(template_name, custom_config)
        
        # Move file to reports directory for download
        if presentation_file and os.path.exists(presentation_file):
            filename = os.path.basename(presentation_file)
            # Copy to reports directory
            reports_filepath = os.path.join(REPORTS_DIR, filename)
            import shutil
            shutil.copy2(presentation_file, reports_filepath)
            download_url = url_for('download_report', filename=filename)
        else:
            return jsonify({'error': 'Failed to generate PowerPoint presentation'}), 500
        
        return jsonify({
            'success': True,
            'download_url': download_url,
            'filename': filename,
            'message': 'PowerPoint presentation generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error generating PowerPoint: {str(e)}")
        return jsonify({'error': f'PowerPoint generation failed: {str(e)}'}), 500


@app.route('/api/powerpoint-templates')
def get_powerpoint_templates():
    """Get available PowerPoint templates"""
    try:
        # Create a generator instance to get template info
        generator = PowerPointGenerator({})  # Empty results for template info
        templates = generator.get_available_templates()
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Error getting PowerPoint templates: {str(e)}")
        return jsonify({'error': f'Failed to get templates: {str(e)}'}), 500


@app.route('/api/powerpoint-color-schemes')
def get_powerpoint_color_schemes():
    """Get available color schemes for PowerPoint"""
    color_schemes = {
        'corporate_blue': {
            'name': 'Corporate Blue',
            'description': 'Professional blue theme for corporate presentations',
            'primary_color': '#1B365D',
            'secondary_color': '#5D737E',
            'accent_color': '#00B894'
        },
        'modern_red': {
            'name': 'Modern Red',
            'description': 'Dynamic red theme for sales presentations',
            'primary_color': '#FF6B6B',
            'secondary_color': '#4ECDC4',
            'accent_color': '#FFE66D'
        },
        'tech_purple': {
            'name': 'Tech Purple',
            'description': 'Modern purple theme for technical presentations',
            'primary_color': '#6C5CE7',
            'secondary_color': '#A29BFE',
            'accent_color': '#00B894'
        },
        'finance_green': {
            'name': 'Finance Green',
            'description': 'Conservative green theme for financial presentations',
            'primary_color': '#2D3436',
            'secondary_color': '#636E72',
            'accent_color': '#00B894'
        },
        'creative_orange': {
            'name': 'Creative Orange',
            'description': 'Vibrant orange theme for creative presentations',
            'primary_color': '#E17055',
            'secondary_color': '#FDCB6E',
            'accent_color': '#6C5CE7'
        }
    }
    
    return jsonify({
        'success': True,
        'color_schemes': color_schemes
    })


# =============================================================================
# COST OPTIMIZER ROUTES  
# =============================================================================

@app.route('/optimize')
def optimize_page():
    """Cost optimizer page"""
    return render_template('cost_optimizer.html')


@app.route('/api/optimize', methods=['POST'])
def optimize_costs():
    """Analyze and optimize costs"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'annual_revenue', 'monthly_orders', 'avg_order_value',
            'labor_costs', 'shipping_costs', 'error_costs',
            'inventory_costs', 'service_investment'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Convert strings to floats
        for field in required_fields:
            try:
                data[field] = float(data[field])
            except (ValueError, TypeError):
                return jsonify({'error': f'Invalid value for {field}: must be a number'}), 400
        
        # Add optional fields
        data['company_name'] = data.get('company_name', 'Client')
        
        # First calculate ROI to get baseline data
        calculator = ROICalculator()
        roi_results = calculator.calculate_roi(data)
        
        # Create ROI data structure for optimizer
        roi_data = {
            'inputs': data,
            'roi_metrics': roi_results.get('roi_metrics', {}),
            'financial_metrics': roi_results.get('financial_metrics', {}),
            'projections': roi_results.get('projections', {})
        }
        
        # Perform cost optimization analysis
        optimizer = CostOptimizer(industry='ecommerce')
        optimization_report = optimizer.analyze_and_optimize(roi_data)
        
        # Get summary for API response
        optimization_summary = optimizer.get_optimization_summary(optimization_report)
        
        # Format recommendations for frontend
        formatted_recommendations = []
        for rec in optimization_report.recommendations[:10]:  # Top 10 recommendations
            formatted_recommendations.append({
                'category': rec.category,
                'savings': rec.potential_savings,
                'priority': rec.priority,
                'description': rec.description,
                'confidence': rec.confidence_score,
                'difficulty': rec.implementation_difficulty,
                'timeframe': rec.timeframe,
                'risk_level': rec.risk_level
            })
        
        return jsonify({
            'success': True,
            'summary': optimization_summary,
            'recommendations': formatted_recommendations,
            'implementation_timeline': optimization_report.implementation_timeline,
            'benchmark_comparison': optimization_report.benchmark_comparison,
            'risk_assessment': optimization_report.risk_assessment,
            'priority_matrix': optimization_report.priority_matrix,
            'detailed_report': optimizer.generate_optimization_report_text(optimization_report)
        })
        
    except Exception as e:
        logger.error(f"Error in cost optimization: {str(e)}")
        return jsonify({'error': f'Optimization failed: {str(e)}'}), 500


@app.route('/api/generate-optimization-report', methods=['POST'])
def generate_optimization_report():
    """Generate detailed optimization report as PDF"""
    try:
        data = request.get_json()
        
        if not data or 'detailed_report' not in data:
            return jsonify({'error': 'Optimization data required'}), 400
        
        # Create PDF report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'cost_optimization_report_{timestamp}.pdf'
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Generate PDF using ReportLab
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph("Cost Optimization Analysis Report", styles['Title']))
        story.append(Spacer(1, 20))
        
        # Content
        report_text = data['detailed_report']
        for paragraph in report_text.split('\n\n'):
            if paragraph.strip():
                if paragraph.strip().isupper():
                    # Headers
                    story.append(Paragraph(paragraph.strip(), styles['Heading2']))
                elif paragraph.strip().startswith('- '):
                    # Bullet points
                    story.append(Paragraph(paragraph.strip(), styles['Normal']))
                else:
                    # Normal text
                    story.append(Paragraph(paragraph.strip(), styles['Normal']))
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        return jsonify({
            'success': True,
            'report_url': url_for('download_report', filename=filename),
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error generating optimization report: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500


@app.route('/api/optimization-benchmarks')
def get_optimization_benchmarks():
    """Get industry benchmarks for cost optimization"""
    try:
        # Sample benchmarks (in production, these would come from database)
        benchmarks = {
            'ecommerce': {
                'small': {
                    'labor_cost_ratio': {'median': 0.18, 'top_quartile': 0.12, 'bottom_quartile': 0.25},
                    'shipping_cost_ratio': {'median': 0.12, 'top_quartile': 0.08, 'bottom_quartile': 0.18},
                    'error_rate': {'median': 0.04, 'top_quartile': 0.02, 'bottom_quartile': 0.07}
                },
                'medium': {
                    'labor_cost_ratio': {'median': 0.15, 'top_quartile': 0.10, 'bottom_quartile': 0.22},
                    'shipping_cost_ratio': {'median': 0.10, 'top_quartile': 0.06, 'bottom_quartile': 0.15},
                    'error_rate': {'median': 0.03, 'top_quartile': 0.015, 'bottom_quartile': 0.05}
                },
                'large': {
                    'labor_cost_ratio': {'median': 0.12, 'top_quartile': 0.08, 'bottom_quartile': 0.18},
                    'shipping_cost_ratio': {'median': 0.07, 'top_quartile': 0.04, 'bottom_quartile': 0.12},
                    'error_rate': {'median': 0.02, 'top_quartile': 0.01, 'bottom_quartile': 0.035}
                }
            }
        }
        
        return jsonify({
            'success': True,
            'benchmarks': benchmarks
        })
        
    except Exception as e:
        logger.error(f"Error getting benchmarks: {str(e)}")
        return jsonify({'error': f'Benchmark retrieval failed: {str(e)}'}), 500


@app.route('/api/cost-optimization-strategies')
def get_cost_optimization_strategies():
    """Get detailed cost optimization strategies"""
    strategies = {
        'labor_optimization': {
            'name': 'Labor Cost Optimization',
            'strategies': [
                {
                    'name': 'Process Automation',
                    'description': 'Automate repetitive tasks using RPA and workflow tools',
                    'potential_savings': '25-40%',
                    'implementation_time': '2-4 months',
                    'difficulty': 'moderate'
                },
                {
                    'name': 'Workforce Optimization',
                    'description': 'Optimize staffing levels and shift scheduling',
                    'potential_savings': '10-20%',
                    'implementation_time': '1-2 months',
                    'difficulty': 'easy'
                },
                {
                    'name': 'Training & Efficiency',
                    'description': 'Improve employee productivity through training programs',
                    'potential_savings': '15-25%',
                    'implementation_time': '3-6 months',
                    'difficulty': 'moderate'
                }
            ]
        },
        'shipping_optimization': {
            'name': 'Shipping Cost Optimization',
            'strategies': [
                {
                    'name': 'Carrier Negotiation',
                    'description': 'Negotiate better rates with shipping carriers',
                    'potential_savings': '10-20%',
                    'implementation_time': '1-3 months',
                    'difficulty': 'easy'
                },
                {
                    'name': 'Zone Skipping',
                    'description': 'Use regional distribution centers to skip zones',
                    'potential_savings': '15-25%',
                    'implementation_time': '6-12 months',
                    'difficulty': 'difficult'
                },
                {
                    'name': 'Packaging Optimization',
                    'description': 'Optimize packaging size and materials',
                    'potential_savings': '8-15%',
                    'implementation_time': '2-4 months',
                    'difficulty': 'moderate'
                }
            ]
        },
        'error_reduction': {
            'name': 'Error Cost Reduction',
            'strategies': [
                {
                    'name': 'Quality Control Systems',
                    'description': 'Implement automated quality control processes',
                    'potential_savings': '60-80%',
                    'implementation_time': '3-6 months',
                    'difficulty': 'moderate'
                },
                {
                    'name': 'System Integration',
                    'description': 'Better integrate systems to reduce data entry errors',
                    'potential_savings': '40-60%',
                    'implementation_time': '4-8 months',
                    'difficulty': 'difficult'
                },
                {
                    'name': 'Employee Training',
                    'description': 'Comprehensive training programs to reduce errors',
                    'potential_savings': '20-40%',
                    'implementation_time': '2-4 months',
                    'difficulty': 'easy'
                }
            ]
        },
        'inventory_optimization': {
            'name': 'Inventory Cost Optimization',
            'strategies': [
                {
                    'name': 'Demand Forecasting',
                    'description': 'AI-powered demand forecasting to optimize stock levels',
                    'potential_savings': '20-35%',
                    'implementation_time': '4-8 months',
                    'difficulty': 'difficult'
                },
                {
                    'name': 'ABC Analysis',
                    'description': 'Categorize inventory by value and velocity',
                    'potential_savings': '10-20%',
                    'implementation_time': '1-3 months',
                    'difficulty': 'easy'
                },
                {
                    'name': 'Supplier Optimization',
                    'description': 'Optimize supplier relationships and terms',
                    'potential_savings': '8-15%',
                    'implementation_time': '3-6 months',
                    'difficulty': 'moderate'
                }
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'strategies': strategies
    })


# =============================================================================
# TEMPLATE MANAGEMENT ROUTES
# =============================================================================

@app.route('/templates')
def templates_page():
    """Template management page"""
    return render_template('templates.html')


@app.route('/api/templates/list')
def list_templates():
    """List all available templates"""
    try:
        category = request.args.get('category')
        tags = request.args.getlist('tags')
        include_predefined = request.args.get('include_predefined', 'true').lower() == 'true'
        include_user = request.args.get('include_user', 'true').lower() == 'true'
        
        templates = template_manager.list_templates(
            category=category,
            include_predefined=include_predefined,
            include_user=include_user,
            tags=tags
        )
        
        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates)
        })
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/templates/create', methods=['POST'])
def create_template():
    """Create a new template"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'template_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate template data
        validation_errors = template_manager.validate_template_data(data['template_data'])
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Template validation failed',
                'validation_errors': validation_errors
            }), 400
        
        # Create template
        result = template_manager.create_template(
            name=data['name'],
            description=data.get('description', ''),
            template_data=data['template_data'],
            category=data.get('category', 'custom'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/templates/<template_id>')
def get_template(template_id):
    """Get a specific template"""
    try:
        template = template_manager.get_template(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
        
        return jsonify({
            'success': True,
            'template': template
        })
        
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing template"""
    try:
        data = request.get_json()
        
        # Validate template data if provided
        if 'template_data' in data:
            validation_errors = template_manager.validate_template_data(data['template_data'])
            if validation_errors:
                return jsonify({
                    'success': False,
                    'error': 'Template validation failed',
                    'validation_errors': validation_errors
                }), 400
        
        result = template_manager.update_template(template_id, data)
        
        return jsonify({
            'success': True,
            'template': result
        })
        
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    try:
        success = template_manager.delete_template(template_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Template deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete template'
            }), 500
            
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/templates/<template_id>/clone', methods=['POST'])
def clone_template(template_id):
    """Clone an existing template"""
    try:
        data = request.get_json()
        new_name = data.get('name')
        
        if not new_name:
            return jsonify({
                'success': False,
                'error': 'New template name is required'
            }), 400
        
        result = template_manager.clone_template(template_id, new_name)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error cloning template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/templates/<template_id>/export')
def export_template(template_id):
    """Export a template"""
    try:
        format_type = request.args.get('format', 'json')
        result = template_manager.export_template(template_id, format_type)
        
        return jsonify({
            'success': True,
            'export': result
        })
        
    except Exception as e:
        logger.error(f"Error exporting template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/templates/import', methods=['POST'])
def import_template():
    """Import a template"""
    try:
        data = request.get_json()
        
        result = template_manager.import_template(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error importing template: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =============================================================================
# BATCH PROCESSING ROUTES
# =============================================================================

@app.route('/batch')
def batch_page():
    """Batch processing page"""
    return render_template('batch.html')


@app.route('/api/batch/upload-csv', methods=['POST'])
def upload_csv_for_batch():
    """Upload CSV file for batch processing"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Process CSV
            mapping = request.form.get('mapping')
            column_mapping = json.loads(mapping) if mapping else None
            
            scenarios = batch_processor.import_from_csv(temp_path, column_mapping)
            
            return jsonify({
                'success': True,
                'scenarios': scenarios,
                'count': len(scenarios),
                'message': f'Imported {len(scenarios)} scenarios successfully'
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error processing CSV upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/batch/upload-excel', methods=['POST'])
def upload_excel_for_batch():
    """Upload Excel file for batch processing"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Process Excel
            sheet_name = request.form.get('sheet_name')
            mapping = request.form.get('mapping')
            column_mapping = json.loads(mapping) if mapping else None
            
            scenarios = batch_processor.import_from_excel(temp_path, sheet_name, column_mapping)
            
            return jsonify({
                'success': True,
                'scenarios': scenarios,
                'count': len(scenarios),
                'message': f'Imported {len(scenarios)} scenarios successfully'
            })
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error processing Excel upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/batch/process', methods=['POST'])
def process_batch_scenarios():
    """Process multiple scenarios in parallel"""
    try:
        data = request.get_json()
        scenarios = data.get('scenarios', [])
        
        if not scenarios:
            return jsonify({
                'success': False,
                'error': 'No scenarios provided'
            }), 400
        
        # Process scenarios
        results = batch_processor.process_scenarios_parallel(scenarios)
        
        # Generate comparison matrix
        comparison_data = batch_processor.generate_comparison_matrix(results)
        
        return jsonify({
            'success': True,
            'results': results,
            'comparison': comparison_data,
            'message': f'Processed {len(scenarios)} scenarios'
        })
        
    except Exception as e:
        logger.error(f"Error processing batch scenarios: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/batch/export-excel', methods=['POST'])
def export_batch_to_excel():
    """Export batch results to Excel"""
    try:
        data = request.get_json()
        comparison_data = data.get('comparison_data')
        
        if not comparison_data:
            return jsonify({
                'success': False,
                'error': 'No comparison data provided'
            }), 400
        
        # Generate Excel file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'batch_analysis_{timestamp}.xlsx'
        filepath = os.path.join(REPORTS_DIR, filename)
        
        batch_processor.export_to_excel(comparison_data, filepath)
        
        return jsonify({
            'success': True,
            'download_url': url_for('download_report', filename=filename),
            'filename': filename,
            'message': 'Excel report generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error exporting batch to Excel: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =============================================================================
# VERSION CONTROL ROUTES
# =============================================================================

@app.route('/versions')
def versions_page():
    """Version control page"""
    return render_template('versions.html')


@app.route('/api/versions/<int:calculation_id>/history')
def get_version_history(calculation_id):
    """Get version history for a calculation"""
    try:
        versions = version_control.get_version_history(calculation_id)
        
        # Convert to serializable format
        serializable_versions = []
        for version in versions:
            version_dict = {
                'version_id': version.version_id,
                'version_number': version.version_number,
                'created_at': version.created_at,
                'created_by': version.created_by,
                'notes': version.notes,
                'changes_count': len(version.changes),
                'checksum': version.checksum
            }
            serializable_versions.append(version_dict)
        
        return jsonify({
            'success': True,
            'versions': serializable_versions,
            'count': len(versions)
        })
        
    except Exception as e:
        logger.error(f"Error getting version history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/versions/<int:calculation_id>/create', methods=['POST'])
def create_version(calculation_id):
    """Create a new version of a calculation"""
    try:
        data = request.get_json()
        
        # Get calculation inputs and results from request or database
        session = get_session()
        calculation = session.query(Calculation).get(calculation_id)
        
        if not calculation:
            session.close()
            return jsonify({
                'success': False,
                'error': 'Calculation not found'
            }), 404
        
        # Use provided data or current calculation data
        inputs = data.get('inputs', {
            'annual_revenue': calculation.annual_revenue,
            'monthly_orders': calculation.monthly_orders,
            'avg_order_value': calculation.avg_order_value,
            'labor_costs': calculation.labor_costs,
            'shipping_costs': calculation.shipping_costs,
            'error_costs': calculation.error_costs,
            'inventory_costs': calculation.inventory_costs,
            'service_investment': calculation.service_investment,
            'company_name': calculation.company_name
        })
        
        results = data.get('results', calculation.results or {})
        notes = data.get('notes', 'Manual version creation')
        
        session.close()
        
        # Create version
        version = version_control.create_version(
            calculation_id=calculation_id,
            inputs=inputs,
            results=results,
            notes=notes
        )
        
        return jsonify({
            'success': True,
            'version': {
                'version_id': version.version_id,
                'version_number': version.version_number,
                'created_at': version.created_at,
                'notes': version.notes
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating version: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/versions/<int:calculation_id>/<int:version_number>')
def get_version(calculation_id, version_number):
    """Get a specific version"""
    try:
        version = version_control.get_version(calculation_id, version_number)
        
        if not version:
            return jsonify({
                'success': False,
                'error': 'Version not found'
            }), 404
        
        return jsonify({
            'success': True,
            'version': {
                'version_id': version.version_id,
                'version_number': version.version_number,
                'inputs': version.inputs,
                'results': version.results,
                'changes': version.changes,
                'notes': version.notes,
                'created_at': version.created_at,
                'created_by': version.created_by,
                'checksum': version.checksum
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting version: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/versions/<int:calculation_id>/compare')
def compare_versions(calculation_id):
    """Compare two versions"""
    try:
        version1 = request.args.get('version1', type=int)
        version2 = request.args.get('version2', type=int)
        
        if not version1 or not version2:
            return jsonify({
                'success': False,
                'error': 'Both version numbers are required'
            }), 400
        
        comparison = version_control.compare_versions(calculation_id, version1, version2)
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
        
    except Exception as e:
        logger.error(f"Error comparing versions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/versions/<int:calculation_id>/rollback', methods=['POST'])
def rollback_version(calculation_id):
    """Rollback to a previous version"""
    try:
        data = request.get_json()
        target_version = data.get('target_version')
        notes = data.get('notes', '')
        
        if not target_version:
            return jsonify({
                'success': False,
                'error': 'Target version is required'
            }), 400
        
        new_version = version_control.rollback_to_version(calculation_id, target_version, notes)
        
        return jsonify({
            'success': True,
            'message': f'Successfully rolled back to version {target_version}',
            'new_version': {
                'version_id': new_version.version_id,
                'version_number': new_version.version_number,
                'created_at': new_version.created_at
            }
        })
        
    except Exception as e:
        logger.error(f"Error rolling back version: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/versions/<int:calculation_id>/audit-trail')
def get_audit_trail(calculation_id):
    """Get audit trail for a calculation"""
    try:
        limit = request.args.get('limit', 50, type=int)
        trail = version_control.get_audit_trail(calculation_id, limit)
        
        return jsonify({
            'success': True,
            'audit_trail': trail,
            'count': len(trail)
        })
        
    except Exception as e:
        logger.error(f"Error getting audit trail: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Create templates directory if running standalone
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # Set template and static folders
    app.template_folder = templates_dir
    app.static_folder = static_dir
    
    PORT = int(os.environ.get('PORT', 8000))
    print("Starting ROI Calculator Web Interface...")
    print(f"Templates directory: {templates_dir}")
    print(f"Static files directory: {static_dir}")
    print(f"Reports directory: {REPORTS_DIR}")
    print(f"Access the calculator at: http://localhost:{PORT}")
    
    app.run(debug=True, host='0.0.0.0', port=PORT)