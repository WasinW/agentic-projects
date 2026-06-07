package com.dataplatform.core

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

case class ValidationRule(
  name: String,
  description: String,
  expression: String,
  severity: String = "ERROR" // ERROR, WARNING, INFO
)

case class ValidationResult(
  ruleName: String,
  passed: Boolean,
  failedRecords: Long,
  totalRecords: Long,
  severity: String,
  message: String
)

class ValidationEngine(spark: SparkSession) {
  
  def validateData(
    df: DataFrame,
    rules: Seq[ValidationRule],
    tableName: String
  ): Seq[ValidationResult] = {
    
    val totalRecords = df.count()
    
    rules.map { rule =>
      try {
        // Apply validation rule
        val validDF = df.filter(rule.expression)
        val validRecords = validDF.count()
        val failedRecords = totalRecords - validRecords
        
        val passed = failedRecords == 0
        val message = if (passed) {
          s"Validation passed: ${rule.description}"
        } else {
          s"Validation failed: ${rule.description}. $failedRecords out of $totalRecords records failed."
        }
        
        ValidationResult(
          ruleName = rule.name,
          passed = passed,
          failedRecords = failedRecords,
          totalRecords = totalRecords,
          severity = rule.severity,
          message = message
        )
        
      } catch {
        case e: Exception =>
          ValidationResult(
            ruleName = rule.name,
            passed = false,
            failedRecords = totalRecords,
            totalRecords = totalRecords,
            severity = "ERROR",
            message = s"Validation rule execution failed: ${e.getMessage}"
          )
      }
    }
  }
  
  def validateSchema(df: DataFrame, expectedSchema: StructType): ValidationResult = {
    val actualSchema = df.schema
    
    val missingFields = expectedSchema.fields.filterNot { expectedField =>
      actualSchema.fields.exists(_.name == expectedField.name)
    }
    
    val extraFields = actualSchema.fields.filterNot { actualField =>
      expectedSchema.fields.exists(_.name == actualField.name)
    }
    
    val typeMismatches = expectedSchema.fields.filter { expectedField =>
      actualSchema.fields.find(_.name == expectedField.name) match {
        case Some(actualField) => actualField.dataType != expectedField.dataType
        case None => false
      }
    }
    
    val passed = missingFields.isEmpty && extraFields.isEmpty && typeMismatches.isEmpty
    
    val message = if (passed) {
      "Schema validation passed"
    } else {
      val issues = Seq(
        if (missingFields.nonEmpty) s"Missing fields: ${missingFields.map(_.name).mkString(", ")}" else "",
        if (extraFields.nonEmpty) s"Extra fields: ${extraFields.map(_.name).mkString(", ")}" else "",
        if (typeMismatches.nonEmpty) s"Type mismatches: ${typeMismatches.map(_.name).mkString(", ")}" else ""
      ).filter(_.nonEmpty)
      
      s"Schema validation failed: ${issues.mkString("; ")}"
    }
    
    ValidationResult(
      ruleName = "schema_validation",
      passed = passed,
      failedRecords = if (passed) 0 else df.count(),
      totalRecords = df.count(),
      severity = "ERROR",
      message = message
    )
  }
  
  def getStandardValidationRules: Seq[ValidationRule] = Seq(
    ValidationRule("not_null_id", "ID field should not be null", "id IS NOT NULL"),
    ValidationRule("positive_amounts", "Amount fields should be positive", "amount > 0"),
    ValidationRule("valid_dates", "Dates should be valid and not in future", "date_column <= current_date()"),
    ValidationRule("no_duplicates", "Records should not have duplicates", "COUNT(*) = COUNT(DISTINCT id)")
  )
}