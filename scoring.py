import pandas as pd
import numpy as np
import requests
import re
import time
from typing import Dict, List, Optional, Tuple
import logging
from urllib.parse import urlparse
import json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedLeadScorer:
    """
    Enhanced Lead Scoring System with improved accuracy and distribution
    Designed for Caprae Capital's PE/M&A lead generation needs
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the Enhanced Lead Scorer"""
        self.openai_api_key = openai_api_key
        
        self.feature_weights = {
            'company_size_score': 0.25,      
            'industry_attractiveness': 0.30,  
            'financial_indicators': 0.25,   
            'technology_stack': 0.10,        
            'market_position': 0.10,        
        }
        
        self.target_industries = {
            # Tier 1 - High Priority (85-95)
            'SaaS': 95, 'Software': 92, 'Technology': 90,
            'Fintech': 88, 'Healthcare Technology': 87, 'E-commerce': 85,
            
            # Tier 2 - Good Targets (70-84)
            'Healthcare': 82, 'Medical Devices': 80, 'Biotechnology': 78,
            'Professional Services': 75, 'Business Services': 73,
            'Manufacturing': 70, 'Industrial': 72,
            
            # Tier 3 - Moderate Interest (55-69)
            'Education': 65, 'EdTech': 68, 'Real Estate': 60,
            'Financial Services': 63, 'Insurance': 58, 'Retail': 55,
            
            # Tier 4 - Lower Priority (35-54)
            'Construction': 50, 'Agriculture': 45, 'Transportation': 48,
            'Energy': 52, 'Utilities': 40, 'Government': 35
        }
        
        self.employee_scoring = {
            (100, 300): 95,  
            (50, 100): 90,   
            (300, 500): 85,   
            (25, 50): 80,     
            (500, 1000): 75,  
            (15, 25): 70,     
            (1000, 2000): 60, 
            (5, 15): 50,      
            (2000, 5000): 40, 
            (0, 5): 30,       
        }
        self.premium_domains = ['.com', '.io', '.ai', '.tech', '.co']
        self.tech_keywords = ['tech', 'soft', 'data', 'cloud', 'ai', 'digital', 'app', 'platform']
        
    def score_leads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main function to score all leads with improved distribution"""
        logger.info(f"Starting enhanced scoring for {len(df)} leads...")

        df_scored = df.copy()
        score_columns = [
            'company_size_score', 'industry_score', 'website_quality_score',
            'financial_score', 'market_position_score', 'composite_score',
            'Score', 'scoring_rationale', 'risk_factors', 'growth_indicators'
        ]
        
        for col in score_columns:
            df_scored[col] = 0 if col != 'scoring_rationale' else ''
        
        for idx, row in df_scored.iterrows():
            try:
                scores = self._score_individual_lead(row)
                
                for key, value in scores.items():
                    if key in df_scored.columns:
                        df_scored.at[idx, key] = value
                
                final_score = self._calculate_enhanced_composite_score(scores, row)
                df_scored.at[idx, 'Score'] = final_score
                
                # Generate detailed rationale
                df_scored.at[idx, 'scoring_rationale'] = self._generate_enhanced_rationale(scores, row)
                df_scored.at[idx, 'risk_factors'] = self._identify_risk_factors(scores, row)
                df_scored.at[idx, 'growth_indicators'] = self._identify_growth_indicators(scores, row)
                
                logger.info(f"Scored lead {idx+1}/{len(df)}: {row.get('Company', 'Unknown')} - Score: {final_score:.1f}")
                
            except Exception as e:
                logger.error(f"Error scoring lead {idx}: {e}")
                df_scored.at[idx, 'Score'] = 45 
                df_scored.at[idx, 'scoring_rationale'] = f"Scoring error: {str(e)}"
        
        df_scored = self._apply_relative_scoring(df_scored)
        df_scored['score_percentile'] = df_scored['Score'].rank(pct=True) * 100
        
        logger.info("Enhanced lead scoring completed!")
        logger.info(f"Score distribution - High (80+): {len(df_scored[df_scored['Score'] >= 80])}, "
                   f"Medium (60-79): {len(df_scored[(df_scored['Score'] >= 60) & (df_scored['Score'] < 80)])}, "
                   f"Low (<60): {len(df_scored[df_scored['Score'] < 60])}")
        
        return df_scored

    def _score_individual_lead(self, row: pd.Series) -> Dict:
        """Enhanced individual lead scoring with more factors"""
        scores = {}
        
        scores['company_size_score'] = self._score_company_size_enhanced(row)
        scores['industry_score'] = self._score_industry_enhanced(row)
        scores['website_quality_score'] = self._score_website_enhanced(row)
        scores['financial_score'] = self._score_financial_enhanced(row)
        scores['market_position_score'] = self._score_market_position_enhanced(row) 
        scores['data_completeness_score'] = self._score_data_completeness(row)
        scores['company_maturity_score'] = self._score_company_maturity(row)
        
        return scores

    def _score_company_size_enhanced(self, row: pd.Series) -> float:
        """Enhanced company size scoring with more nuanced approach"""
        employee_count = row.get('EmployeeCount', 0)
        
        try:
            emp_count = int(employee_count) if pd.notna(employee_count) else 0
        except:
            emp_count = 0
            
        if emp_count == 0:
            return 25  
        
        for (min_emp, max_emp), base_score in self.employee_scoring.items():
            if min_emp <= emp_count < max_emp:
                range_position = (emp_count - min_emp) / (max_emp - min_emp)
                if range_position > 0.7:  
                    return min(base_score + 3, 100)
                elif range_position < 0.3:  
                    return max(base_score - 3, 0)
                return base_score
        
        if emp_count >= 5000:
            return 25  # Too large for typical PE
        
        return 35

    def _score_industry_enhanced(self, row: pd.Series) -> float:
        """Enhanced industry scoring with partial matching and context"""
        industry = row.get('Industry', '')
        
        if not industry or pd.isna(industry):
            return 40  
            
        industry_clean = str(industry).strip().title()
        industry_lower = industry_clean.lower()
        
        if industry_clean in self.target_industries:
            base_score = self.target_industries[industry_clean]
        else:
            best_match_score = 45 
            best_match_weight = 0
            
            for target_industry, score in self.target_industries.items():
                target_lower = target_industry.lower()
                
                if target_lower in industry_lower or industry_lower in target_lower:
                    if len(target_lower) > best_match_weight:
                        best_match_score = score * 0.9 
                        best_match_weight = len(target_lower)
                
                target_words = target_lower.split()
                industry_words = industry_lower.split()
                
                common_words = set(target_words) & set(industry_words)
                if common_words and len(common_words) / len(target_words) > 0.5:
                    match_score = score * 0.8
                    if match_score > best_match_score:
                        best_match_score = match_score
            
            base_score = best_match_score
        
        if any(keyword in industry_lower for keyword in ['tech', 'software', 'digital', 'ai', 'data']):
            base_score = min(base_score + 5, 100)
        
        if any(keyword in industry_lower for keyword in ['service', 'consulting', 'solution']):
            base_score = min(base_score + 3, 100)
            
        return base_score

    def _score_website_enhanced(self, row: pd.Series) -> float:
        """Enhanced website quality assessment"""
        website = row.get('Website', '')
        
        if not website or pd.isna(website):
            return 20
        
        score = 40  
        
        try:
            website_str = str(website).strip().lower()
            if not website_str.startswith(('http://', 'https://')):
                website_str = 'https://' + website_str
            
            parsed = urlparse(website_str)
            domain = parsed.netloc.lower()
            
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                domain_name = domain_parts[0]
                domain_ext = '.' + domain_parts[-1]
                
                if domain_ext in ['.com']:
                    score += 20
                elif domain_ext in ['.io', '.ai', '.tech', '.co']:
                    score += 25  # Tech-forward domains
                elif domain_ext in ['.net', '.org']:
                    score += 10
                else:
                    score += 5
                
                if 4 <= len(domain_name) <= 12: 
                    score += 15
                elif 3 <= len(domain_name) <= 15:
                    score += 10
                
                tech_score = sum(5 for keyword in self.tech_keywords if keyword in domain_name)
                score += min(tech_score, 15)
                
                if any(char.isdigit() for char in domain_name):
                    score -= 5
                if '-' in domain_name:
                    score -= 3
                
                if domain_name.isalpha() and len(domain_name) >= 5:
                    score += 5
                    
        except Exception as e:
            logger.warning(f"Error analyzing website {website}: {e}")
            score = 25
        
        return max(min(score, 100), 0)

    def _score_financial_enhanced(self, row: pd.Series) -> float:
        """Enhanced financial scoring with multiple indicators"""
        score = 45  
        
        if 'Revenue' in row and pd.notna(row['Revenue']):
            try:
                revenue = float(row['Revenue'])
                if revenue >= 100_000_000:
                    score = 95
                elif revenue >= 50_000_000:
                    score = 90
                elif revenue >= 25_000_000:
                    score = 85
                elif revenue >= 10_000_000:
                    score = 80
                elif revenue >= 5_000_000:
                    score = 75
                elif revenue >= 1_000_000:
                    score = 70
                elif revenue >= 500_000:
                    score = 60
                else:
                    score = 50
            except:
                pass
        
        if 'Growth' in row and pd.notna(row['Growth']):
            try:
                growth = float(row['Growth'])
                if growth >= 100:  
                    score += 25
                elif growth >= 50:
                    score += 20
                elif growth >= 25:
                    score += 15
                elif growth >= 10:
                    score += 10
                elif growth >= 0:
                    score += 5
                elif growth >= -10:
                    score -= 5
                else:
                    score -= 15
            except:
                pass
        
        if 'Profit' in row and pd.notna(row['Profit']):
            try:
                profit = float(row['Profit'])
                if profit > 0:
                    score += 10
                else:
                    score -= 5
            except:
                pass
        
        return max(min(score, 100), 0)

    def _score_market_position_enhanced(self, row: pd.Series) -> float:
        """Enhanced market position scoring"""
        score = 45
        
        company_name = str(row.get('Company', '')).lower()
        industry = str(row.get('Industry', '')).lower()
        
        leadership_terms = ['leader', 'leading', 'premier', 'top', 'best', 'first', '#1', 'market leader']
        leadership_score = sum(8 for term in leadership_terms if term in company_name)
        score += min(leadership_score, 20)
        
        innovation_terms = ['ai', 'tech', 'digital', 'cloud', 'data', 'analytics', 'automation', 'platform', 'saas']
        innovation_score = sum(4 for term in innovation_terms if term in company_name)
        score += min(innovation_score, 16)
        
        if any(term in industry for term in ['software', 'tech', 'saas']):
            score += 12
        elif any(term in industry for term in ['healthcare', 'medical', 'fintech']):
            score += 8
        
        if len(company_name.split()) <= 3 and company_name.replace(' ', '').isalnum():
            score += 5
        
        return max(min(score, 100), 0)

    def _score_data_completeness(self, row: pd.Series) -> float:
        """Score based on data completeness"""
        required_fields = ['Company', 'Industry', 'Website', 'EmployeeCount']
        optional_fields = ['Revenue', 'Growth', 'Founded', 'Location']
        
        required_score = sum(20 for field in required_fields if field in row and pd.notna(row[field]) and row[field] != '')
        optional_score = sum(5 for field in optional_fields if field in row and pd.notna(row[field]) and row[field] != '')
        
        return min(required_score + optional_score, 100)

    def _score_company_maturity(self, row: pd.Series) -> float:
        """Score company maturity indicators"""
        score = 50
        
        if 'Founded' in row and pd.notna(row['Founded']):
            try:
                founded_year = int(row['Founded'])
                current_year = datetime.now().year
                company_age = current_year - founded_year
                
                if 5 <= company_age <= 15:  # Sweet spot
                    score += 20
                elif 3 <= company_age <= 20:
                    score += 10
                elif company_age > 25:
                    score -= 10
            except:
                pass
        
        return score

    def _calculate_enhanced_composite_score(self, scores: Dict, row: pd.Series) -> float:
        """Calculate composite score with enhanced logic"""
        
        weighted_score = 0
        total_weight = 0
        
        core_scores = {
            'company_size_score': self.feature_weights['company_size_score'],
            'industry_score': self.feature_weights['industry_attractiveness'],
            'financial_score': self.feature_weights['financial_indicators'],
            'website_quality_score': self.feature_weights['technology_stack'],
            'market_position_score': self.feature_weights['market_position'],
        }
        
        for score_key, weight in core_scores.items():
            if score_key in scores:
                weighted_score += scores[score_key] * weight
                total_weight += weight
        
        if total_weight > 0:
            base_score = weighted_score / total_weight
        else:
            base_score = 45
        
        if 'data_completeness_score' in scores:
            completeness_factor = scores['data_completeness_score'] / 100
            base_score = base_score * (0.85 + 0.15 * completeness_factor)
        
        final_score = self._apply_enhanced_adjustments(base_score, scores, row)     
        return round(max(min(final_score, 100), 0), 1)

    def _apply_enhanced_adjustments(self, base_score: float, scores: Dict, row: pd.Series) -> float:
        """Apply enhanced bonus/penalty logic"""
        adjusted_score = base_score
        
        high_scores = [s for s in scores.values() if isinstance(s, (int, float)) and s >= 85]
        if len(high_scores) >= 3:
            adjusted_score += 8
        elif len(high_scores) >= 2:
            adjusted_score += 4
        
        score_values = [s for s in scores.values() if isinstance(s, (int, float)) and s > 0]
        if len(score_values) >= 4:
            std_dev = np.std(score_values)
            if std_dev < 12: 
                adjusted_score += 5
            elif std_dev < 20:  
                adjusted_score += 2
        
        critical_scores = ['industry_score', 'company_size_score']
        critical_failures = sum(1 for score_key in critical_scores 
                              if scores.get(score_key, 50) < 40)
        adjusted_score -= critical_failures * 8
        
        if scores.get('website_quality_score', 50) < 25:
            adjusted_score -= 12
        
        if scores.get('data_completeness_score', 50) < 40:
            adjusted_score -= 8
        
        if (scores.get('industry_score', 0) >= 80 and 
            scores.get('company_size_score', 0) >= 80):
            adjusted_score += 6
        
        return adjusted_score

    def _apply_relative_scoring(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply relative scoring to improve distribution"""
        scores = df['Score'].values
        
        percentiles = np.percentile(scores, [10, 25, 50, 75, 90])
        
        def adjust_score(score):
            if score >= percentiles[4]: 
                return min(score + 5, 100)
            elif score >= percentiles[3]: 
                return min(score + 2, 100)
            elif score <= percentiles[0]: 
                return max(score - 5, 0)
            elif score <= percentiles[1]: 
                return max(score - 2, 0)
            return score
        
        df['Score'] = df['Score'].apply(adjust_score)
        return df

    def _generate_enhanced_rationale(self, scores: Dict, row: pd.Series) -> str:
        """Generate detailed scoring rationale"""
        rationale_parts = []
        
        size_score = scores.get('company_size_score', 0)
        emp_count = row.get('EmployeeCount', 0)
        if size_score >= 85:
            rationale_parts.append(f"Optimal size ({emp_count} employees) for PE investment")
        elif size_score >= 70:
            rationale_parts.append(f"Good company size ({emp_count} employees)")
        elif size_score < 50:
            rationale_parts.append(f"Size concerns ({emp_count} employees)")
        
        industry_score = scores.get('industry_score', 0)
        industry = row.get('Industry', 'Unknown')
        if industry_score >= 85:
            rationale_parts.append(f"High-priority industry ({industry})")
        elif industry_score >= 70:
            rationale_parts.append(f"Attractive industry ({industry})")
        elif industry_score < 55:
            rationale_parts.append(f"Lower-priority industry ({industry})")
        
        financial_score = scores.get('financial_score', 0)
        if financial_score >= 80:
            rationale_parts.append("Strong financial profile")
        elif financial_score < 50:
            rationale_parts.append("Limited financial data")
        
        web_score = scores.get('website_quality_score', 0)
        if web_score >= 70:
            rationale_parts.append("Strong digital presence")
        elif web_score < 40:
            rationale_parts.append("Weak digital footprint")
        
        return "; ".join(rationale_parts) if rationale_parts else "Standard analysis applied"

    def _identify_risk_factors(self, scores: Dict, row: pd.Series) -> str:
        """Identify potential risk factors"""
        risks = []
        
        if scores.get('company_size_score', 50) < 40:
            risks.append("Size mismatch")
        
        if scores.get('industry_score', 50) < 50:
            risks.append("Industry challenges")
        
        if scores.get('financial_score', 50) < 50:
            risks.append("Financial uncertainty")
        
        if scores.get('data_completeness_score', 50) < 60:
            risks.append("Limited data")
        
        return "; ".join(risks) if risks else "Low risk profile"

    def _identify_growth_indicators(self, scores: Dict, row: pd.Series) -> str:
        """Identify growth potential indicators"""
        indicators = []
        
        if scores.get('industry_score', 0) >= 85:
            indicators.append("High-growth industry")
        
        if scores.get('market_position_score', 0) >= 70:
            indicators.append("Strong market position")
        
        if 'Growth' in row and pd.notna(row['Growth']):
            try:
                growth = float(row['Growth'])
                if growth > 25:
                    indicators.append(f"High growth rate ({growth}%)")
            except:
                pass
        
        return "; ".join(indicators) if indicators else "Standard growth potential"

def score_leads(df: pd.DataFrame, openai_api_key: str = None) -> pd.DataFrame:
    """
    Enhanced main function to score leads with improved accuracy
    
    Args:
        df: DataFrame with lead data
        openai_api_key: Optional OpenAI API key
    
    Returns:
        DataFrame with enhanced scores and analysis
    """
    
    scorer = ImprovedLeadScorer(openai_api_key=openai_api_key)
    scored_df = scorer.score_leads(df)
    
    return scored_df

if __name__ == "__main__":
    sample_data = {
        'Company': ['TechCorp Inc', 'Manufacturing Co', 'SaaS Startup', 'Healthcare Solutions', 'Small Consulting'],
        'Industry': ['Technology', 'Manufacturing', 'SaaS', 'Healthcare', 'Professional Services'],
        'Website': ['techcorp.com', 'manufacturing.net', 'saasapp.io', 'healthsolutions.com', 'consulting.biz'],
        'EmployeeCount': [150, 500, 75, 200, 12],
        'Revenue': [25000000, 50000000, 5000000, 15000000, 800000]
    }
    
    df = pd.DataFrame(sample_data)
    scored_df = score_leads(df)
    
    print("Enhanced Scoring Results:")
    print(scored_df[['Company', 'Score', 'company_size_score', 'industry_score', 'scoring_rationale']].head())