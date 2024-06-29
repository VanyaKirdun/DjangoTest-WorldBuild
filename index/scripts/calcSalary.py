
def calcSalary(workedHoursData, buildObject, positionSalary):
  totalSalary = 0
  for key in workedHoursData:
    mounthHours = 0
    for indexKey in workedHoursData[key]:
      mounthHours += int(workedHoursData[key][indexKey])
    totalSalary += int(mounthHours) * positionSalary * buildObject[int(indexKey)-1].allowance
      
  return totalSalary