use structopt::StructOpt;
use secp256k1::{SecretKey};

mod error;
use error::Error;

#[derive(StructOpt, Debug)]
#[structopt(name = "calculate_cli", about = "Calculate digest command line tool.", version = "0.1.0")]
struct Opt {
    #[structopt(subcommand)]
    cmd: Command
}

#[derive(Debug, StructOpt)]
enum Command {
    /// sign message
    #[structopt(name="sign")]
    Sign(SignOpt)
}

#[derive(Debug, StructOpt)]
struct SignOpt {
    pri_key: String,
    message: String,
}

fn sign_msg(params :&SignOpt) -> Result<(), Error>{
    
    let secret_key = SecretKey::from_slice(&[0xcd; 32]).expect("32 bytes, within curve order");

    signer.update(data).unwrap();
    let signature = signer.sign_to_vec().unwrap();
}

// fn read_file()

fn main() {
    let opt = Opt::from_args();
    match opt.cmd {
        Command::Sign(params) => sign_msg(&params),
        _ => ()
    }
}