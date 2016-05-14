#!"C:\xampp\perl\bin\perl.exe"

use CGI qw(:standard);
use strict;

use Carp;
use HTML::LinkExtor;
use HTTP::Request;
use HTTP::Response;
use HTTP::Status;
use LWP::RobotUA;

$| = 1;
my $ROBOT_NAME = 'ggirald1Bot/1.0';
my $ROBOT_MAIL = 'ggirald1@jhu.edu';
my $ROBOT_DELAY_IN_MINUTES = 0.0001;

my $robot = new LWP::RobotUA $ROBOT_NAME, $ROBOT_MAIL;

$robot->delay( $ROBOT_DELAY_IN_MINUTES);

my @websites = ( "http://www.rock30games.com/ItemSearch--search-",
	"http://www.gamestop.com/browse?nav=16k-3-", "http://www.ebay.com/sch/i.html?_from=R40&_trksid=p2050601.m570.l1313.TR10.TRC0.A0.H0.Xcall+of+duty.TRS0&_nkw=");
my @product_links;
my @product_costs;
my @product_names;
my $game;
print header;
print<<END;
    <h1 align = "center"> Video Game Shopper </h1>
    <form>
        <div align="center">
            <input type="text" name="game">
            <input type="submit" value="Search">
        </div>
    </form>
END

if(param()){
	$game = param('game');
	if(ok()){
		search_websites();
		sort_results();
		print_results();
	}
}

sub ok{
	my $fine = 1;
	if(!$game){
		print "<p align='center'>Your Search is Empty!</p>",br; $fine = 0; 
	}
	return $fine;
}

sub print_results{
	print "<ul style = 'list-style-type:none;'>\n";
	for(my $i = 0;$i<@websites;$i++){
		my $caption;
		if($websites[$i] =~ /rock30games/){
			$caption = "Rock 30 Games";
		}
		elsif($websites[$i] =~ /gamestop/){
			$caption = "Game Stop";
		}
		else{
			$caption = "Ebay";
		}
		print "<li>\n<table>\n<caption><h2 align='left'><u>$caption</u></h2></caption>\n";
		if(!$product_links[$i]){
			print "<tr><td>No Search Results Found </td></tr>\n";
		}
		else{
			print "<tr>\n<th>Rank</th>\n<th>Cost</th>\n<th>Link</th>\n</tr>";
			for(my $j = 0; $j < 10;$j++){
				my $place = $j+1;
				print "<tr>\n<td>$place</td>\n<td>\$$product_costs[$i][$j]</td>\n<td><a href='$product_links[$i][$j]'>$product_names[$i][$j]</td>\n</tr>\n";
			}
		}
		print"</table>\n</li>\n";
	}
	print "</ul>"
}
sub sort_results{
	for(my $i = 0; $i<@websites; $i++){
		for(my $j = 0; $j< scalar @{$product_links[$i]};$j++){
			my $min_index = $j;
			for( my $k = $j+1; $k< scalar @{$product_links[$i]};$k++){
				my $cost_1 = $product_costs[$i][$k];
				my $cost_2 = $product_costs[$i][$min_index];
				if($cost_1< $cost_2){
					$min_index = $k;
				}
			}
			my $temp_cost = $product_costs[$i][$j];
			my $temp_link = $product_links[$i][$j];
			my $temp_name = $product_names[$i][$j];
			$product_costs[$i][$j]=$product_costs[$i][$min_index];
			$product_links[$i][$j]=$product_links[$i][$min_index];
			$product_names[$i][$j]=$product_names[$i][$min_index];
			$product_costs[$i][$min_index]=$temp_cost;
			$product_links[$i][$min_index]=$temp_link;
			$product_names[$i][$min_index]=$temp_name;
		}
	}
}
sub search_websites {
	#for each of our websites we want to get info from
	for(my $i = 0; $i < @websites; $i++){
		#append the key words formed from the user's query to the search url
		my @split_search = split / /,$game;
		my $keywords="";
		for(my $j = 0; $j<@split_search;$j++){
			if($j == 0){
				$keywords =$keywords.$split_search[$j];
			}
			else{
				if($websites[$i] =~ /rock30games/){
				$keywords = $keywords."-".$split_search[$j];
				}
				else{
				$keywords = $keywords."+".$split_search[$j];
				}
			}
		}
		my $request;
		if($websites[$i] =~/gamestop/){
			$request = new HTTP::Request HEAD => $websites[$i].$keywords.",28zu0";
		} 
        if ($websites[$i] =~/ebay/) {
            $request = new HTTP::Request HEAD => $websites[$i].$keywords."&_sacat=1249";
        }
        if ($websites[$i] =~ /rock30games/) {
        	$request = new HTTP::Request HEAD => $websites[$i].$keywords."--srcin-1";
        }
		my $response = $robot -> request($request);
		#print $response->code,br;
		next if $response -> code != RC_OK;

		$request->method('GET');
		$response = $robot ->request($request);

		if($response -> code != RC_OK){
			print "url rejected";
			next;
		}
		my $related_urls = &grab_urls($response->content,$i);
		&extract_prices($response->content,$i);
	}
}
sub grab_urls {

    my $content = shift;
    my $i = shift;

     my $index = 0;
  skip:
    while ($content =~ s/<\s*[aA] ([^>]*)>\s*(?:<[^>]*>)*(?:([^<]*)(?:<[^aA>]*>)*<\/\s*[aA]\s*>)?//) {

	my $tag_text = $1;
	my $reg_text = $2;
	my $link = "";

	if (defined $reg_text) {
	    $reg_text =~ s/[\n\r]/ /;
	    $reg_text =~ s/\s{2,}/ /;
	}
	# make sure we are hitting url and it is not self-reference
	if ($tag_text =~ /href\s*=\s*(?:["']([^"']*)["']|([^\s])*)/i and $tag_text !~ /#/) {
	    $link = $1 || $2;
	    if($reg_text =~ /$game/i){
			if($websites[$i] =~ /gamestop/){
				$product_links[$i][$index] = "http://www.gamestop.com".$link;
			}
			elsif($websites[$i] =~ /ebay/){
				$product_links[$i][$index] = $link;
			}
			else {
				$product_links[$i][$index] = $link;
			}
			
	    	$product_names[$i][$index] = $reg_text;
	    	$index++;
	    }
	}
    }

}
sub extract_prices{
	my $content = shift;
	my $i = shift;
    if ($websites[$i] =~ /gamestop/) {
	   	my @costs = $content =~ /<p class="pricing ats-product-price">(.*)<\/p>/g;
	   	my $j = 0;
	    for my $cost(@costs) {
	   		my @costs = split /\$/, $cost;
	        if($costs[2]){
	       		$cost = $costs[2];
	      	} else {
	       		$cost = $costs[1];
	       	}
	       	$product_costs[$i][$j] =$cost;
		    $j++;
	   	}
    }
	elsif($websites[$i] =~ /ebay/){
		my @costs = $content =~ /\$[0-9]+\.[0-9]+/g;
		my $j = 0;
		for my $cost(@costs) {
			my @costs = split /\$/, $cost;
			$cost = $costs[1];
			$product_costs[$i][$j]=$cost;
			$j++;
		}
	}
	elsif($websites[$i] =~ /rock30games/){
		my @costs = $content =~ /\$[0-9]+\.[0-9]+/g;
		my $j = 0;
		for my $cost(@costs){
			my @costs = split /\$/, $cost;
			$cost = $costs[1];
			$product_costs[$i][$j]=$cost;
			$j++;
		}
	}
}