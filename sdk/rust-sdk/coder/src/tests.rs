// use port_ethabi::execute;
pub type Uint = ethereum_types::U256;

fn main() {
    // some tests
    let value = "-8916561";
    let abs = Uint::from_dec_str(value.trim_start_matches('-')).unwrap();
    let max = Uint::max_value() / 2;
    println!("[+] Uint max value = {}", max);

    let int = if value.starts_with('-') {
        if abs.is_zero() {
            println!("[-] zero number");
        } else if abs > max + 1 {
            println!("[-] int256 parse error: Underflow");
        }
        !abs + 1 // two's complement
    } else {
        if abs > max {
            println!("[-] int256 parse error: Overflow");
        }
        abs
    };
    println!("[+] ret = {}", int);


    // encode lenient
    // 
    // let command = "ethabi encode params -v int256[10] [4902102,11467818,-8731461,-5489313,-8916561,7676978,7732408,5651870,1931581,-4507333] --lenient".split(' ');
    // println!("[+] {:?}", command);
    // println!("[+] {}", execute(command).unwrap());

    // let command = "ethabi encode params -v int256[][] [[4902102,11467818,-8731461,-5489313,-8916561,7676978,7732408,5651870,1931581,-4507333],[4902102,11467818,-8731461,-5489313,-8916561,7676978,7732408,5651870,1931581,-4507333],[4902102,11467818,-8731461,-5489313,-8916561,7676978,7732408,5651870,1931581,-4507333]] --lenient".split(' ');
    // println!("[+] {:?}", command);
    // println!("[+] {}", execute(command).unwrap());

    // encode strict
    // 
    // let command = "ethabi encode params -v int256[10] [4902102,11467818,-8731461,-5489313,-8916561,7676978,7732408,5651870,1931581,-4507333]".split(' ');
    // println!("[+] {:?}", command);
    // println!("[+] {}", execute(command).unwrap());

    // decode
    // let command = "ethabi decode params -t int256[] 0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000004accd60000000000000000000000000000000000000000000000000000000000aefc2affffffffffffffffffffffffffffffffffffffffffffffffffffffffff7ac4bbffffffffffffffffffffffffffffffffffffffffffffffffffffffffffac3d5fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff77f1af0000000000000000000000000000000000000000000000000000000000752432000000000000000000000000000000000000000000000000000000000075fcb80000000000000000000000000000000000000000000000000000000000563d9e00000000000000000000000000000000000000000000000000000000001d793dffffffffffffffffffffffffffffffffffffffffffffffffffffffffffbb393b".split(' ');
    // println!("[+] {}", execute(command).unwrap());
}