"use client";
// import {DatePicker} from "@heroui/date-picker";
import { Button, DatePicker } from "@heroui/react";
import { DateTime } from "luxon";

import { now, getLocalTimeZone } from "@internationalized/date";
import { get } from "http";
import { useState } from "react";

export const TimeUtil = () => {
  const [current, setCurrent] = useState(now(getLocalTimeZone()));
console.log(current);
  return (
    <div>
      <div className="flex flex-row items-center justify-center gap-4">
        <DatePicker
          showMonthAndYearPickers
          value={current}
          label="Event Date"
          variant="bordered"
          granularity="second"
          onChange={(date) => setCurrent(date)}
        />
        <Button onPress={() => setCurrent(now(getLocalTimeZone()))}>
          Refresh
        </Button>
      </div>
    </div>
  );
};
