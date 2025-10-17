#!/usr/bin/env python3
"""CLI for analytics and statistics calculations."""

import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.goal_value import GoalValueCalculator, GoalValueAnalyzer, EventGoalValueUpdater, PlayerStatsGoalValueUpdater


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='FBRef Analytics Calculator')
    parser.add_argument('--calculate-goal-value', action='store_true',
                       help='Calculate goal value statistics')
    parser.add_argument('--update-goal-values', action='store_true',
                       help='Update goal_value field for all existing goal events')
    parser.add_argument('--update-player-stats', action='store_true',
                       help='Update goal_value and gv_avg fields for all player stats records')
    parser.add_argument('--show-dataframe', action='store_true',
                       help='Display goal value data as DataFrame for visualization')
    parser.add_argument('--show-sample-sizes', action='store_true',
                       help='Show sample sizes organized by minute')
    parser.add_argument('--minute', type=int, metavar='N',
                       help='Show detailed sample sizes for specific minute N')
    parser.add_argument('--window-size', type=int, default=5, metavar='N',
                       help='Window size for smoothing (default: 5)')
    parser.add_argument('--score-diff', type=int, metavar='N',
                       help='Show sample sizes for specific score_diff N')
    parser.add_argument('--show-goal-details', action='store_true',
                       help='Show detailed information about individual goals')
    
    args = parser.parse_args()
    
    if args.calculate_goal_value:
        calculator = GoalValueCalculator()
        calculator.run()
    
    elif args.update_goal_values:
        updater = EventGoalValueUpdater()
        updater.run()
    
    elif args.update_player_stats:
        updater = PlayerStatsGoalValueUpdater()
        updater.run()
    
    elif args.show_dataframe:
        analyzer = GoalValueAnalyzer()
        df = analyzer.export_to_dataframe()
        print("Goal Value DataFrame:")
        print(df)
        print(f"\nDataFrame shape: {df.shape}")
        print(f"Non-null values: {df.count().sum()}")
    
    elif args.show_sample_sizes:
        analyzer = GoalValueAnalyzer()
        analyzer.show_sample_sizes(args.minute, args.window_size, args.score_diff)
    
    elif args.show_goal_details:
        analyzer = GoalValueAnalyzer()
        analyzer.show_goal_details(args.minute, args.score_diff, args.window_size)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
