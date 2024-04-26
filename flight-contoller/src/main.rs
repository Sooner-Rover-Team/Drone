#![no_std]
#![no_main]

use esp_backtrace as _;
use esp_println::println;
use esp_hal::{gpio::IO, peripherals::Peripherals, prelude::*};
#[entry]
fn main() -> ! {
    let peripherals = Peripherals::take();
    let _system = peripherals.SYSTEM.split();
    let io = IO::new(peripherals.GPIO, peripherals.IO_MUX);
    let button = io.pins.gpio10.into_pull_up_input();
    let mut led = io.pins.gpio12.into_push_pull_output();

    esp_println::logger::init_logger_from_env();

    loop {
        if button.is_high(){
            led.set_high();
            println!("button pressed!✅");
        } else {
            led.set_low();
            println!("button not pressed!❌");
        }
        
    }
}
