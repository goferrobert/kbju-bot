from typing import Dict, Optional, Tuple
import math

def calculate_body_fat(
    gender: str,
    weight: float,
    height: float,
    waist: float,
    neck: float,
    hip: Optional[float] = None
) -> float:
    """
    Calculate body fat percentage using the US Navy method.
    
    Args:
        gender: 'male' or 'female'
        weight: weight in kg
        height: height in cm
        waist: waist circumference in cm
        neck: neck circumference in cm
        hip: hip circumference in cm (required for females)
    
    Returns:
        Body fat percentage
    """
    if gender.lower() == 'male':
        # Male formula
        body_fat = 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)) - 450
    else:
        # Female formula
        if hip is None:
            raise ValueError("Hip measurement is required for female body fat calculation")
        body_fat = 495 / (1.29579 - 0.35004 * math.log10(waist + hip - neck) + 0.22100 * math.log10(height)) - 450
    
    return round(max(0, min(100, body_fat)), 1)

def calculate_bmr(
    gender: str,
    weight: float,
    height: float,
    age: int,
    activity_level: str
) -> Tuple[float, float]:
    """
    Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    and Total Daily Energy Expenditure (TDEE).
    
    Args:
        gender: 'male' or 'female'
        weight: weight in kg
        height: height in cm
        age: age in years
        activity_level: 'sedentary', 'light', 'moderate', 'active', or 'very_active'
    
    Returns:
        Tuple of (BMR, TDEE) in calories
    """
    # BMR calculation
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.2,      # Little or no exercise
        'light': 1.375,        # Light exercise 1-3 days/week
        'moderate': 1.55,      # Moderate exercise 3-5 days/week
        'active': 1.725,       # Hard exercise 6-7 days/week
        'very_active': 1.9     # Very hard exercise & physical job
    }
    
    tdee = bmr * activity_multipliers.get(activity_level.lower(), 1.2)
    return round(bmr), round(tdee)

def calculate_macros(
    tdee: float,
    goal: str,
    weight: float,
    activity_level: str
) -> Dict[str, int]:
    """
    Calculate macronutrient distribution based on goals.
    
    Args:
        tdee: Total Daily Energy Expenditure
        goal: 'weight_loss', 'maintenance', or 'muscle_gain'
        weight: weight in kg
        activity_level: activity level for protein adjustment
    
    Returns:
        Dictionary with calories and macronutrient targets
    """
    # Calorie adjustment based on goal
    if goal == 'weight_loss':
        calories = tdee - 500  # 500 calorie deficit
    elif goal == 'muscle_gain':
        calories = tdee + 300  # 300 calorie surplus
    else:  # maintenance
        calories = tdee
    
    # Protein calculation (1.6-2.2g per kg of bodyweight)
    protein_multiplier = 2.0 if activity_level in ['active', 'very_active'] else 1.6
    protein = round(weight * protein_multiplier)
    
    # Fat calculation (20-35% of calories)
    fat = round((calories * 0.25) / 9)  # 25% of calories from fat
    
    # Carb calculation (remaining calories)
    carb = round((calories - (protein * 4) - (fat * 9)) / 4)
    
    return {
        'calories': round(calories),
        'protein': protein,
        'fat': fat,
        'carbs': carb
    }

def calculate_ideal_weight(
    height: float,
    gender: str,
    body_type: str
) -> float:
    """
    Calculate ideal weight based on height, gender and body type.
    
    Args:
        height: height in cm
        gender: 'male' or 'female'
        body_type: 'athletic', 'slim', or 'healthy'
    
    Returns:
        Ideal weight in kg
    """
    # Base calculation using Devine formula
    if gender.lower() == 'male':
        base_weight = 50 + 2.3 * ((height - 152.4) / 2.54)
    else:
        base_weight = 45.5 + 2.3 * ((height - 152.4) / 2.54)
    
    # Adjust for body type
    adjustments = {
        'athletic': 1.1,  # 10% more for athletic build
        'slim': 0.9,      # 10% less for slim build
        'healthy': 1.0    # No adjustment for healthy build
    }
    
    return round(base_weight * adjustments.get(body_type.lower(), 1.0), 1)

def calculate_activity_score(
    steps: int,
    training_frequency: int,
    training_intensity: str
) -> float:
    """
    Calculate activity score based on steps and training.
    
    Args:
        steps: daily steps
        training_frequency: training sessions per week
        training_intensity: 'low', 'medium', or 'high'
    
    Returns:
        Activity score (0-100)
    """
    # Steps score (0-50 points)
    steps_score = min(50, (steps / 10000) * 50)
    
    # Training score (0-50 points)
    intensity_multipliers = {
        'low': 0.5,
        'medium': 0.75,
        'high': 1.0
    }
    training_score = min(50, (training_frequency / 7) * 50 * intensity_multipliers.get(training_intensity.lower(), 0.5))
    
    return round(steps_score + training_score, 1)

def calculate_progress(
    current_weight: float,
    start_weight: float,
    current_body_fat: float,
    start_body_fat: float,
    days: int
) -> Dict[str, float]:
    """
    Calculate progress metrics.
    
    Args:
        current_weight: current weight in kg
        start_weight: starting weight in kg
        current_body_fat: current body fat percentage
        start_body_fat: starting body fat percentage
        days: number of days since start
    
    Returns:
        Dictionary with progress metrics
    """
    weight_change = current_weight - start_weight
    body_fat_change = current_body_fat - start_body_fat
    
    # Calculate lean mass changes
    start_lean = start_weight * (1 - start_body_fat/100)
    current_lean = current_weight * (1 - current_body_fat/100)
    lean_change = current_lean - start_lean
    
    # Calculate daily averages
    daily_weight_change = weight_change / days if days > 0 else 0
    daily_body_fat_change = body_fat_change / days if days > 0 else 0
    
    return {
        'weight_change': round(weight_change, 1),
        'body_fat_change': round(body_fat_change, 1),
        'lean_mass_change': round(lean_change, 1),
        'daily_weight_change': round(daily_weight_change, 2),
        'daily_body_fat_change': round(daily_body_fat_change, 2)
    } 